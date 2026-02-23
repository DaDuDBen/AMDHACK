"""NLP parser with LLM switching and deterministic regex fallback."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from anthropic import AsyncAnthropic

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
    "sodium hydroxide",
    "nitric acid",
    "water",
    "potassium",
    "sodium",
    "ammonia",
    "ethanol",
    "glycerol",
}


def _normalize_reactant_name(raw: str) -> str:
    aliases = {
        "hcl": "hydrochloric acid",
        "muriatic acid": "hydrochloric acid",
        "lye": "sodium hydroxide",
        "naoh": "sodium hydroxide",
        "h2so4": "sulphuric acid",
    }
    value = raw.strip().lower()
    return aliases.get(value, value)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _fallback_regex_parse(user_input: str) -> dict[str, Any]:
    lowered = user_input.lower()
    action = "mix"
    for keyword in _ACTION_KEYWORDS:
        if keyword in lowered:
            action = "add_to" if keyword == "add to" else keyword
            break

    reactants = sorted({_normalize_reactant_name(name) for name in _COMMON_REACTANTS if name in lowered})
    if len(reactants) < 2:
        noun_candidates = re.findall(r"\b([a-z]+(?:\s+[a-z]+){0,2})\b", lowered)
        for chunk in noun_candidates:
            if any(token in chunk for token in ("acid", "oxide", "sulphate", "nitrate", "chloride", "water")):
                reactants.append(_normalize_reactant_name(chunk))
        reactants = sorted({item for item in reactants if item})[:4]

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


async def _parse_with_ollama(user_input: str) -> dict[str, Any]:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "phi3:mini")
    prompt = f"{PARSER_SYSTEM_PROMPT}\n\nStudent input: {user_input}"

    async with httpx.AsyncClient(timeout=10.0) as client:
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

    parser = _parse_with_claude if llm_mode == "claude" else _parse_with_ollama

    for attempt in range(2):
        try:
            result = await parser(user_input)
            result["raw_input"] = user_input
            if "conditions" not in result or not isinstance(result["conditions"], dict):
                result["conditions"] = {"temperature": "room", "concentration": None, "quantity_notes": None}
            return result
        except json.JSONDecodeError:
            if attempt == 1:
                return _fallback_regex_parse(user_input)
        except (httpx.TimeoutException, TimeoutError):
            return _fallback_regex_parse(user_input)
        except Exception:
            if attempt == 1:
                return _fallback_regex_parse(user_input)

    return _fallback_regex_parse(user_input)
