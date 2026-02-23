"""Socratic explanation engine with LLM and template fallback paths."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx
from anthropic import AsyncAnthropic

EXPLANATION_SYSTEM_PROMPT = """You are Prayog, a friendly chemistry tutor for Indian school students (Class 8-12).
You explain reactions clearly and simply, using examples from everyday Indian life where possible.
You follow the Socratic method — after explaining what happened, always ask one guiding question
that makes the student think deeper about WHY it happened.
Keep explanations under 100 words. Use simple English.
Reference NCERT chapters when relevant.
Always return ONLY valid JSON with keys: what_happened, socratic_question, key_concept, ncert_reference, fun_fact."""


def _template_fallback(simulation_result: dict[str, Any]) -> dict[str, str]:
    reactants = ", ".join(simulation_result.get("reactants", [])) or "the given reactants"
    products = ", ".join(simulation_result.get("products", [])) or "new products"
    reaction_type = simulation_result.get("type", "chemical reaction").replace("_", " ").title()
    return {
        "what_happened": f"When {reactants} were combined, they formed {products} as a {reaction_type}.",
        "socratic_question": "Which reactant do you think changed role most, and what observation supports that?",
        "key_concept": reaction_type,
        "ncert_reference": simulation_result.get("ncert_reference", "Class 10, Chapter 1: Chemical Reactions and Equations"),
        "fun_fact": "Many industrial processes use the same reaction patterns but under carefully controlled conditions.",
    }


async def _generate_with_claude(prompt: str) -> dict[str, Any]:
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        temperature=0.2,
        system=EXPLANATION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    content = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
    return json.loads(content.strip())


async def _generate_with_ollama(prompt: str) -> dict[str, Any]:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "phi3:mini")
    llm_prompt = f"{EXPLANATION_SYSTEM_PROMPT}\n\n{prompt}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": llm_prompt, "stream": False},
        )
        response.raise_for_status()
        payload = response.json()
    return json.loads(payload.get("response", "{}"))


async def generate_explanation(
    simulation_result: dict[str, Any],
    student_input: str,
    difficulty_level: str = "class_10",
) -> dict[str, Any]:
    """Generate Socratic explanation from selected LLM, with fallback templates."""
    llm_mode = os.getenv("LLM_MODE", "offline").lower()
    if llm_mode == "offline":
        return _template_fallback(simulation_result)

    prompt = (
        f"Student input: {student_input}\n"
        f"Difficulty level: {difficulty_level}\n"
        f"Simulation result: {json.dumps(simulation_result, ensure_ascii=False)}"
    )

    generator = _generate_with_claude if llm_mode == "claude" else _generate_with_ollama
    try:
        explanation = await generator(prompt)
        required_keys = {"what_happened", "socratic_question", "key_concept", "ncert_reference", "fun_fact"}
        if not required_keys.issubset(explanation.keys()):
            return _template_fallback(simulation_result)
        return explanation
    except Exception:
        return _template_fallback(simulation_result)
