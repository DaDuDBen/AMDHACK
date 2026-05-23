"""API route definitions for Prayog-Shala backend."""

from __future__ import annotations

import logging
import os

import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from core.explanation_engine import generate_explanation
from core.nlp_parser import parse_experiment
from core.safety_filter import check_safety
from core.simulation_engine import REACTIONS_DB, simulate
from core.visualization_mapper import get_visualization
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

logger = logging.getLogger(__name__)
router = APIRouter()

OLLAMA_TIMEOUT_SECONDS = 10.0

_runtime_llm_mode: str | None = None


def _llm_mode() -> str:
    if _runtime_llm_mode is not None:
        return _runtime_llm_mode
    return os.getenv("LLM_MODE", "offline").strip().lower() or "offline"


async def _ensure_ollama_available() -> bool:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT_SECONDS) as client:
            response = await client.get(f"{base_url}/api/tags")
            response.raise_for_status()
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout):
        return False
    except httpx.HTTPError:
        return False
    return True


@router.post("/api/experiment", response_model=SuccessResponse | BlockedResponse | UnknownResponse)
async def run_experiment(payload: ExperimentRequest):
    # 1) Safety check must happen first — deterministic, no LLM
    safety_result = check_safety(payload.user_input)
    if not safety_result.get("is_safe", True):
        return BlockedResponse(
            safety=SafetyPayload(
                reason=safety_result.get("reason") or "Blocked for safety reasons",
                educational_note=safety_result.get("educational_note") or "",
                severity=safety_result.get("severity") or "warning",
            )
        )

    # 2) Check Ollama availability if in ollama mode
    if _llm_mode() == "ollama" and not await _ensure_ollama_available():
        return JSONResponse(status_code=503, content={"error": "Offline LLM unavailable, set LLM_MODE=offline"})

    # 3) Parse the student input via LLM or regex fallback
    parsed = await parse_experiment(payload.user_input)

    reactants = parsed.get("reactants") or []
    action = parsed.get("action")

    # 4) Follow-up question detection:
    #    If no reactants found BUT context from a previous experiment exists,
    #    route to explanation engine as a follow-up question.
    if not reactants and payload.context:
        logger.info("Detected follow-up question with context")
        explanation = await generate_explanation(
            simulation_result=payload.context,
            student_input=payload.user_input,
            difficulty_level=payload.context.get("difficulty_level", "class_10"),
            is_followup=True,
        )

        return SuccessResponse(
            is_followup=True,
            explanation=ExplanationPayload(**explanation),
            parsed_input={
                "reactants": [],
                "action": "followup",
                "conditions": {},
            },
        )

    # 5) No reactants, no context → can't understand
    if not reactants:
        return JSONResponse(status_code=400, content={"error": "Could not understand input"})

    # 6) Simulation — 100% local, uses reactions.json only
    simulation = simulate(parsed)
    if not simulation.get("found"):
        partial_info = simulation.get("partial_info") or {"reactant_notes": {}}
        return UnknownResponse(
            message="This reaction isn't in our database yet.",
            partial_info={"reactant_notes": partial_info.get("reactant_notes", {})},
        )

    simulation_payload = SimulationPayload(
        reaction_id=simulation["reaction_id"],
        balanced_equation=simulation["balanced_equation"],
        reactants=simulation["reactants"],
        products=simulation["products"],
        observations=simulation["observations"],
        thermodynamics=simulation["thermodynamics"],
        type=simulation.get("type", ""),
    )

    # 7) Visualization + explanation
    visualization = get_visualization(simulation)
    explanation = await generate_explanation(
        simulation_result=simulation,
        student_input=payload.user_input,
        difficulty_level=simulation.get("difficulty_level", "class_10"),
    )

    visualization_payload = VisualizationPayload(
        animation_asset=visualization["animation_asset"],
        show_thermometer=visualization["show_thermometer"],
        thermometer_direction=visualization.get("thermometer_direction") or "steady",
        intensity=visualization["intensity"],
    )
    explanation_payload = ExplanationPayload(**explanation)

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


@router.post("/api/mode")
async def switch_mode(body: dict):
    """Switch LLM mode at runtime (for demo purposes)."""
    new_mode = body.get("mode", "").strip().lower()
    valid_modes = {"claude", "ollama", "groq", "offline"}
    if new_mode not in valid_modes:
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid mode. Valid modes: {', '.join(sorted(valid_modes))}"},
        )

    global _runtime_llm_mode
    _runtime_llm_mode = new_mode
    logger.info("LLM mode switched to: %s", new_mode)

    return {
        "status": "ok",
        "llm_mode": new_mode,
        "message": f"LLM mode switched to {new_mode}",
    }
