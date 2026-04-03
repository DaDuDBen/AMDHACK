"""NLP parser with LLM switching and deterministic regex fallback."""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

import httpx

logger = logging.getLogger(__name__)

PARSER_SYSTEM_PROMPT = """You are a chemistry lab assistant that parses student experiment instructions into structured JSON.
Extract the reactants, action, and conditions from the student's input.
Normalize chemical names to their common IUPAC or textbook names (e.g., "muriatic acid" → "hydrochloric acid", "lye" → "sodium hydroxide").
Always return ONLY valid JSON. No explanation, no markdown, no preamble."""

_ACTION_KEYWORDS = ("mix", "add", "heat", "burn", "dissolve", "add to")
_COMMON_REACTANTS = {
    "magnesium",
    "hydrochloric acid",
    "zinc",
    "sulphuric acid",
    "iron",
    "copper sulphate",
    "copper sulphate solution",
    "sodium hydroxide",
    "nitric acid",
    "water",
    "potassium",
    "sodium",
    "ammonia",
    "ethanol",
    "glycerol",
    "calcium carbonate",
    "calcium oxide",
    "silver nitrate",
    "sodium chloride",
    "lead nitrate",
    "potassium iodide",
    "barium chloride",
    "copper",
    "aluminium",
    "hydrogen peroxide",
    "litmus",
    "universal indicator",
    "methane",
    "carbon",
    "oxygen",
    "hydrogen",
    "ferrous sulphate",
    "sodium carbonate",
    "acetic acid",
    "sodium bicarbonate",
}

_ALIAS_MAP: dict[str, str] = {
    "hcl": "hydrochloric acid",
    "muriatic acid": "hydrochloric acid",
    "lye": "sodium hydroxide",
    "naoh": "sodium hydroxide",
    "h2so4": "sulphuric acid",
    "sulfuric acid": "sulphuric acid",
    "caco3": "calcium carbonate",
    "limestone": "calcium carbonate",
    "marble": "calcium carbonate",
    "chalk": "calcium carbonate",
    "quicklime": "calcium oxide",
    "cao": "calcium oxide",
    "baking soda": "sodium bicarbonate",
    "nahco3": "sodium bicarbonate",
    "vinegar": "acetic acid",
    "table salt": "sodium chloride",
    "nacl": "sodium chloride",
    "mg": "magnesium",
    "zn": "zinc",
    "fe": "iron",
    "cu": "copper",
    "al": "aluminium",
    "aluminum": "aluminium",
    "agno3": "silver nitrate",
    "cuso4": "copper sulphate",
    "copper sulfate": "copper sulphate",
    "feso4": "ferrous sulphate",
    "na2co3": "sodium carbonate",
    "washing soda": "sodium carbonate",
    "h2o2": "hydrogen peroxide",
    "h2o": "water",
    "o2": "oxygen",
    "h2": "hydrogen",
    "n2": "nitrogen",
    "ch4": "methane",
    "magnesium ribbon": "magnesium",
    "iron nail": "iron",
    "iron filings": "iron",
    "zinc granules": "zinc",
    "zinc strip": "zinc",
    "copper wire": "copper",
    "copper strip": "copper",
    "aluminium foil": "aluminium",
    "dilute hydrochloric acid": "hydrochloric acid",
    "dilute sulphuric acid": "sulphuric acid",
    "dilute hcl": "hydrochloric acid",
    "dilute h2so4": "sulphuric acid",
}


def _normalize_reactant_name(raw: str) -> str:
    value = raw.strip().lower()
    return _ALIAS_MAP.get(value, value)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _fallback_regex_parse(user_input: str) -> dict[str, Any]:
    lowered = user_input.lower()
    action = None
    for keyword in _ACTION_KEYWORDS:
        if keyword in lowered:
            action = "add_to" if keyword == "add to" else keyword
            break

    # Check multi-word reactants first (longest match wins)
    found: set[str] = set()
    sorted_reactants = sorted(_COMMON_REACTANTS, key=len, reverse=True)
    for name in sorted_reactants:
        if name in lowered:
            normalized = _normalize_reactant_name(name)
            found.add(normalized)

    # Also check aliases
    for alias, canonical in _ALIAS_MAP.items():
        if alias in lowered:
            found.add(canonical)

    reactants = sorted(found)[:4]

    concentration = "dilute" if "dilute" in lowered else "concentrated" if "concentrated" in lowered else None
    temperature = "heated" if "heat" in lowered or "heated" in lowered else "room"
    quantity_notes = None
    if "small" in lowered:
        quantity_notes = "small quantity"

    return {
        "reactants": reactants,
        "action": action,
        "conditions": {
            "temperature": temperature,
            "concentration": concentration,
            "quantity_notes": quantity_notes,
        },
        "raw_input": user_input,
        "parsed_by": "fallback_regex",
    }


async def _parse_with_claude(user_input: str) -> dict[str, Any]:
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        temperature=0,
        system=PARSER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_input}],
    )
    content = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
    return _extract_json(content)


async def _parse_with_groq(user_input: str) -> dict[str, Any]:
    from groq import AsyncGroq

    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    response = await client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": PARSER_SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
    )
    content = response.choices[0].message.content or "{}"
    return _extract_json(content)


async def _parse_with_ollama(user_input: str) -> dict[str, Any]:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "chemistry-mistral-7b")
    prompt = f"{PARSER_SYSTEM_PROMPT}\n\nStudent input: {user_input}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        payload = response.json()
    return _extract_json(payload.get("response", ""))


async def parse_experiment(user_input: str) -> dict[str, Any]:
    """Parse free-text student instruction into structured reaction input."""
    llm_mode = os.getenv("LLM_MODE", "offline").lower()

    if llm_mode == "offline":
        return _fallback_regex_parse(user_input)

    if llm_mode == "claude":
        parser = _parse_with_claude
    elif llm_mode == "groq":
        parser = _parse_with_groq
    else:
        parser = _parse_with_ollama

    for attempt in range(2):
        try:
            result = await parser(user_input)
            result["raw_input"] = user_input
            if "conditions" not in result or not isinstance(result["conditions"], dict):
                result["conditions"] = {"temperature": "room", "concentration": None, "quantity_notes": None}
            # Normalize reactant names from LLM output
            if "reactants" in result and isinstance(result["reactants"], list):
                result["reactants"] = [_normalize_reactant_name(r) for r in result["reactants"]]
            return result
        except json.JSONDecodeError:
            logger.warning("LLM returned malformed JSON (attempt %d)", attempt + 1)
            if attempt == 1:
                return _fallback_regex_parse(user_input)
        except (httpx.TimeoutException, TimeoutError):
            logger.warning("LLM timeout, falling back to regex parser")
            return _fallback_regex_parse(user_input)
        except Exception:
            logger.warning("LLM error (attempt %d), retrying", attempt + 1, exc_info=True)
            if attempt == 1:
                return _fallback_regex_parse(user_input)

    return _fallback_regex_parse(user_input)
