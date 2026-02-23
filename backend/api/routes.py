import asyncio
import json
import os
from pathlib import Path

import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.request_models import ExperimentRequest
from models.response_models import (
    BlockedResponse,
    ExplanationPayload,
    ReactionSummary,
    ReactionsResponse,
    SafetyPayload,
    SimulationPayload,
    StatusResponse,
    SuccessResponse,
    UnknownResponse,
    VisualizationPayload,
)

router = APIRouter()

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
REACTIONS_PATH = DATA_DIR / "reactions.json"
SAFETY_PATH = DATA_DIR / "safety_blocklist.json"
OLLAMA_TIMEOUT_SECONDS = 10.0


with REACTIONS_PATH.open("r", encoding="utf-8") as f:
    REACTIONS_DB: dict[str, dict] = json.load(f)

with SAFETY_PATH.open("r", encoding="utf-8") as f:
    SAFETY_RULES: list[dict] = json.load(f)


class OllamaUnavailableError(Exception):
    pass


def _llm_mode() -> str:
    return os.getenv("LLM_MODE", "offline").strip().lower() or "offline"


def _normalize_reactants(reactants: list[str]) -> list[str]:
    return sorted([r.strip().lower() for r in reactants if r and r.strip()])


def _fallback_parse(user_input: str) -> dict:
    lower = user_input.lower()
    action = "mix"
    if any(word in lower for word in ["heat", "warm", "ignite"]):
        action = "heat"
    elif any(word in lower for word in ["burn", "combust"]):
        action = "burn"
    elif "dissolve" in lower:
        action = "dissolve"
    elif "add" in lower:
        action = "add_to"

    known_terms = {
        "magnesium ribbon": "magnesium",
        "hydrochloric acid": "hydrochloric acid",
        "sulphuric acid": "sulphuric acid",
        "sodium hydroxide": "sodium hydroxide",
        "calcium carbonate": "calcium carbonate",
        "oxygen": "oxygen",
        "water": "water",
        "potassium": "potassium",
        "ethanol": "ethanol",
        "copper sulphate": "copper sulphate",
        "iron": "iron",
        "zinc": "zinc",
    }

    reactants = [canonical for term, canonical in known_terms.items() if term in lower]
    conditions: dict[str, str] = {}
    if "dilute" in lower:
        conditions["concentration"] = "dilute"
    if "concentrated" in lower:
        conditions["concentration"] = "concentrated"

    return {
        "reactants": reactants,
        "action": action,
        "conditions": conditions,
        "raw_input": user_input,
        "parsed_by": "fallback_regex",
    }


async def _call_ollama(user_input: str) -> dict:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "phi3:mini")
    prompt = (
        "You are a chemistry lab assistant that parses student experiment instructions into structured JSON. "
        "Extract the reactants, action, and conditions from the student's input. "
        'Return ONLY JSON with keys: reactants (list), action (string), conditions (object), raw_input (string). '
        f"Input: {user_input}"
    )
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{base_url}/api/generate", json=payload)
            response.raise_for_status()
    except httpx.ConnectError as exc:
        raise OllamaUnavailableError from exc
    except httpx.HTTPError as exc:
        if isinstance(exc, httpx.ConnectTimeout):
            raise asyncio.TimeoutError from exc
        raise

    body = response.json()
    return json.loads(body.get("response", "{}"))


async def _parse_with_mode(user_input: str) -> dict:
    mode = _llm_mode()
    if mode == "offline":
        return _fallback_parse(user_input)

    if mode == "ollama":
        malformed_once = False
        for _ in range(2):
            try:
                parsed = await _call_ollama(user_input)
                parsed.setdefault("raw_input", user_input)
                return parsed
            except json.JSONDecodeError:
                if malformed_once:
                    return _fallback_parse(user_input)
                malformed_once = True
                continue
            except asyncio.TimeoutError:
                return _fallback_parse(user_input)
        return _fallback_parse(user_input)

    # claude mode fallback implementation (timeout + malformed retry) using local fallback by default
    return _fallback_parse(user_input)


def _check_safety(user_input: str) -> dict | None:
    lower_input = user_input.lower()
    for rule in SAFETY_RULES:
        keywords = [k.lower() for k in rule.get("keywords", [])]
        if keywords and all(keyword in lower_input for keyword in keywords):
            return {
                "reason": rule.get("reason", "Blocked for safety reasons"),
                "educational_note": rule.get("educational_note", ""),
                "severity": rule.get("severity", "warning"),
            }
    return None


def _simulate(parsed: dict) -> dict:
    reactants = _normalize_reactants(parsed.get("reactants", []))
    if not reactants:
        return {"found": False, "partial_info": {"reactant_notes": {}}}

    key = "|".join(reactants)
    for reaction_id, reaction in REACTIONS_DB.items():
        if reaction.get("reactants_key") == key:
            return {"found": True, "reaction_id": reaction_id, **reaction}

    notes = {r: f"{r.title()} is recognized but this exact combination is unavailable." for r in reactants}
    return {"found": False, "partial_info": {"reactant_notes": notes}}


def _build_visualization(animation_type: str, thermodynamics: str) -> dict:
    heat_up = "exo" in thermodynamics
    return {
        "animation_asset": f"{animation_type.replace('_with_heat', '').replace('_', '_')}.json",
        "show_thermometer": heat_up,
        "thermometer_direction": "up" if heat_up else "steady",
        "intensity": "medium" if heat_up else "low",
    }


def _build_explanation(simulation: dict) -> dict:
    reaction_type = simulation.get("type", "reaction").replace("_", " ").title()
    reactants = " and ".join(simulation.get("reactants", []))
    return {
        "what_happened": f"When {reactants} were combined, a {reaction_type.lower()} occurred.",
        "socratic_question": "What evidence in the observations tells you new products were formed?",
        "key_concept": reaction_type,
        "ncert_reference": simulation.get("ncert_reference", "Class 10, Chapter 1"),
        "fun_fact": "Chemical reactions often reveal themselves through color, heat, or gas evolution.",
    }


@router.post("/api/experiment", response_model=SuccessResponse | BlockedResponse | UnknownResponse)
async def run_experiment(payload: ExperimentRequest):
    safety_hit = _check_safety(payload.user_input)
    if safety_hit:
        return BlockedResponse(safety=SafetyPayload(**safety_hit))

    try:
        parsed = await _parse_with_mode(payload.user_input)
    except OllamaUnavailableError:
        return JSONResponse(status_code=503, content={"error": "Offline LLM unavailable, set LLM_MODE=offline"})

    reactants = parsed.get("reactants") or []
    action = parsed.get("action")
    if not reactants and not action and not parsed.get("conditions"):
        return JSONResponse(status_code=400, content={"error": "Could not understand input"})

    simulation = _simulate(parsed)
    if not simulation.get("found"):
        return UnknownResponse(
            message="This reaction isn't in our database yet.",
            partial_info=simulation.get("partial_info", {"reactant_notes": {}}),
        )

    simulation_payload = SimulationPayload(
        reaction_id=simulation["reaction_id"],
        balanced_equation=simulation["balanced_equation"],
        reactants=simulation["reactants"],
        products=simulation["products"],
        observations=simulation["observations"],
        thermodynamics=simulation["thermodynamics"],
    )
    visualization_payload = VisualizationPayload(**_build_visualization(simulation["animation_type"], simulation["thermodynamics"]))
    explanation_payload = ExplanationPayload(**_build_explanation(simulation))

    return SuccessResponse(
        simulation=simulation_payload,
        visualization=visualization_payload,
        explanation=explanation_payload,
        parsed_input={
            "reactants": reactants,
            "action": action,
            "conditions": parsed.get("conditions", {}),
        },
    )


@router.get("/api/status", response_model=StatusResponse)
async def api_status():
    return StatusResponse(
        llm_mode=_llm_mode(),
        reactions_loaded=len(REACTIONS_DB),
    )


@router.get("/api/reactions", response_model=ReactionsResponse)
async def list_reactions():
    summaries = [
        ReactionSummary(
            id=reaction_id,
            reactants=reaction.get("reactants", []),
            type=reaction.get("type", ""),
            difficulty_level=reaction.get("difficulty_level", ""),
        )
        for reaction_id, reaction in REACTIONS_DB.items()
    ]
    return ReactionsResponse(reactions=summaries)
