"""Socratic explanation engine with LLM and template fallback paths."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

EXPLANATION_SYSTEM_PROMPT = """You are Prayog, a friendly chemistry tutor for Indian school students (Class 8-12).
You explain reactions clearly and simply, using examples from everyday Indian life where possible.
You follow the Socratic method — after explaining what happened, always ask one guiding question
that makes the student think deeper about WHY it happened.
Keep explanations under 100 words. Use simple English.
Use LaTeX wrapped in $ signs for all chemical formulas (e.g. $\\mathrm{H_2O}$, $\\mathrm{CO_2}$).
Reference NCERT chapters when relevant.
Always return ONLY valid JSON with keys: what_happened, socratic_question, key_concept, ncert_reference, fun_fact."""

# Reaction-type-specific templates for better offline explanations
_TYPE_TEMPLATES: dict[str, dict[str, str]] = {
    "single_displacement": {
        "socratic_question": "Which metal is more reactive here, and how can you tell from the reactivity series?",
        "key_concept": "Single Displacement Reaction & Reactivity Series",
        "fun_fact": "The reactivity series was first established by experiments just like this one!",
    },
    "neutralization": {
        "socratic_question": "What would happen to the pH if you added more acid than base?",
        "key_concept": "Neutralization — Acid + Base → Salt + Water",
        "fun_fact": "Antacids you take for acidity work by the same neutralization reaction!",
    },
    "double_displacement": {
        "socratic_question": "Can you predict what the precipitate would be based on solubility rules?",
        "key_concept": "Double Displacement & Precipitation",
        "fun_fact": "Water treatment plants use precipitation reactions to remove impurities.",
    },
    "combustion": {
        "socratic_question": "What do all combustion reactions have in common as a requirement?",
        "key_concept": "Combustion Reactions — Fire Triangle",
        "fun_fact": "The fuel in your kitchen gas stove undergoes the same type of reaction!",
    },
    "combination": {
        "socratic_question": "Why do you think the product has different properties than the reactants?",
        "key_concept": "Combination (Synthesis) Reactions",
        "fun_fact": "Cement setting is a combination reaction that takes days to complete.",
    },
    "combination_combustion": {
        "socratic_question": "Why is the flame so bright? What does the color tell you about temperature?",
        "key_concept": "Combustion of Metals in Air",
        "fun_fact": "Magnesium flares are used in emergency signaling because the flame is so bright!",
    },
    "decomposition": {
        "socratic_question": "What type of energy input was needed to break down this compound?",
        "key_concept": "Decomposition Reactions — Breaking Bonds",
        "fun_fact": "Limestone kilns have used thermal decomposition for thousands of years to make quicklime!",
    },
    "precipitation": {
        "socratic_question": "If the precipitate sinks, what does that tell you about its density?",
        "key_concept": "Precipitation — Formation of Insoluble Products",
        "fun_fact": "Photography once relied on silver halide precipitation on film!",
    },
    "indicator_test": {
        "socratic_question": "What molecular change causes the indicator to change color?",
        "key_concept": "Acid-Base Indicators & pH",
        "fun_fact": "You can make a natural indicator at home using red cabbage juice!",
    },
    "special": {
        "socratic_question": "What makes this reaction unusual compared to typical patterns?",
        "key_concept": "Special Reactions in Chemistry",
        "fun_fact": "Many important industrial processes use reactions that don't fit neatly into textbook categories.",
    },
}

_OBSERVATION_DESCRIPTIONS: dict[str, str] = {
    "effervescence": "bubbles forming (a gas is being released)",
    "vigorous effervescence": "rapid bubbling shows a gas is being produced quickly",
    "slow effervescence": "gentle bubbling indicates a slow gas release",
    "solid dissolves": "the solid reactant is being consumed by the reaction",
    "heat produced": "the container warming up means the reaction releases energy",
    "temperature rises": "heat release indicates an exothermic reaction",
}


def _template_fallback(simulation_result: dict[str, Any]) -> dict[str, str]:
    reactants = ", ".join(simulation_result.get("reactants", [])) or "the given reactants"
    products = ", ".join(simulation_result.get("products", [])) or "new products"
    reaction_type = simulation_result.get("type", "chemical reaction")
    reaction_type_display = reaction_type.replace("_", " ").title()

    # Build a richer description from observations
    observations = simulation_result.get("observations", [])
    obs_text = ""
    if observations:
        obs_text = f" You can observe: {', '.join(observations)}."

    thermo = simulation_result.get("thermodynamics", "")
    thermo_text = ""
    if "exothermic" in thermo:
        thermo_text = " The reaction releases heat (exothermic)."
    elif "endothermic" in thermo:
        thermo_text = " The reaction absorbs heat (endothermic)."

    gas = simulation_result.get("gas_produced")
    gas_text = f" {gas.replace('_', ' ').title()} gas is produced." if gas else ""

    type_info = _TYPE_TEMPLATES.get(reaction_type, _TYPE_TEMPLATES["special"])

    return {
        "what_happened": (
            f"When {reactants} were combined, they formed {products} "
            f"through a {reaction_type_display} reaction.{obs_text}{thermo_text}{gas_text}"
        ),
        "socratic_question": type_info["socratic_question"],
        "key_concept": type_info["key_concept"],
        "ncert_reference": simulation_result.get(
            "ncert_reference", "Class 10, Chapter 1: Chemical Reactions and Equations"
        ),
        "fun_fact": type_info["fun_fact"],
    }


def _followup_template(simulation_result: dict[str, Any], question: str) -> dict[str, str]:
    """Generate a template-based answer for follow-up questions when LLM is unavailable."""
    lowered = question.lower()
    thermo = simulation_result.get("thermodynamics", "")
    reaction_type = simulation_result.get("type", "chemical reaction").replace("_", " ")

    # Common follow-up patterns
    if "warm" in lowered or "hot" in lowered or "heat" in lowered or "exothermic" in lowered or "endothermic" in lowered:
        return {
            "what_happened": (
                f"The reaction is {thermo.replace('_', ' ')}. When bonds form in the products, "
                f"they release energy as heat — that's why the container feels warm. "
                f"The total energy of the products is lower than the reactants."
            ),
            "socratic_question": "If we measured the temperature before and after, how many degrees do you think it would rise?",
            "key_concept": "Exothermic Reactions & Bond Energy",
            "ncert_reference": simulation_result.get("ncert_reference", ""),
            "fun_fact": "Hand warmers use exothermic reactions (iron oxidation) to generate heat!",
        }
    elif "bubble" in lowered or "gas" in lowered or "fizz" in lowered:
        gas = simulation_result.get("gas_produced", "a gas")
        return {
            "what_happened": (
                f"The bubbles you see are {gas.replace('_', ' ')} escaping from the solution. "
                f"During the {reaction_type}, one of the products is a gas that doesn't dissolve well in the liquid."
            ),
            "socratic_question": "How could you test which gas is being produced?",
            "key_concept": "Gas Evolution in Chemical Reactions",
            "ncert_reference": simulation_result.get("ncert_reference", ""),
            "fun_fact": "The 'pop test' with a burning splint is how we identify hydrogen gas in labs!",
        }
    elif "color" in lowered or "colour" in lowered:
        return {
            "what_happened": (
                f"The color change happens because the products have different light-absorbing "
                f"properties than the reactants. Different metal ions produce different colors in solution."
            ),
            "socratic_question": "What do you think the color tells us about the ions present?",
            "key_concept": "Color Changes & Transition Metal Chemistry",
            "ncert_reference": simulation_result.get("ncert_reference", ""),
            "fun_fact": "Fireworks get their colors from different metal salts — copper gives blue, strontium gives red!",
        }
    else:
        # Generic follow-up
        return {
            "what_happened": (
                f"This is a {reaction_type} reaction. "
                f"The key observations are: {', '.join(simulation_result.get('observations', ['chemical change occurs']))}."
            ),
            "socratic_question": "What would change if we altered the concentration or temperature?",
            "key_concept": simulation_result.get("type", "").replace("_", " ").title(),
            "ncert_reference": simulation_result.get("ncert_reference", ""),
            "fun_fact": "Scientists use the same observation skills you're building right now to discover new reactions!",
        }


def _strip_code_fences(text: str) -> str:
    import re
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


async def _generate_with_claude(prompt: str) -> dict[str, Any]:
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        temperature=0.2,
        system=EXPLANATION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    content = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
    return json.loads(_strip_code_fences(content))


async def _generate_with_groq(prompt: str) -> dict[str, Any]:
    from groq import AsyncGroq

    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    response = await client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": EXPLANATION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content or "{}"
    # Strip markdown fences if present
    content = content.strip()
    if content.startswith("```"):
        import re

        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    return json.loads(content.strip())


async def _generate_with_ollama(prompt: str) -> dict[str, Any]:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "chemistry-mistral-7b")
    llm_prompt = f"{EXPLANATION_SYSTEM_PROMPT}\n\n{prompt}"

    async with httpx.AsyncClient(timeout=60.0) as client:
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
    is_followup: bool = False,
) -> dict[str, Any]:
    """Generate Socratic explanation from selected LLM, with fallback templates."""
    llm_mode = os.getenv("LLM_MODE", "offline").lower()
    if llm_mode == "offline":
        if is_followup:
            return _followup_template(simulation_result, student_input)
        return _template_fallback(simulation_result)

    if is_followup:
        prompt = (
            f"Student follow-up question: {student_input}\n"
            f"Previous reaction context: {json.dumps(simulation_result, ensure_ascii=False)}\n"
            f"Difficulty level: {difficulty_level}\n"
            f"Answer the student's follow-up about the previous reaction. "
            f"Provide a comprehensive, detailed explanation (up to 200-300 words). "
            f"Explicitly ignore the 100-word limit from the system prompt for this follow-up, "
            f"as the student needs a thorough understanding."
        )
    else:
        prompt = (
            f"Student input: {student_input}\n"
            f"Difficulty level: {difficulty_level}\n"
            f"Simulation result: {json.dumps(simulation_result, ensure_ascii=False)}"
        )

    if llm_mode == "claude":
        generator = _generate_with_claude
    elif llm_mode == "groq":
        generator = _generate_with_groq
    else:
        generator = _generate_with_ollama

    try:
        explanation = await generator(prompt)
        required_keys = {"what_happened", "socratic_question", "key_concept", "ncert_reference", "fun_fact"}
        if not required_keys.issubset(explanation.keys()):
            logger.warning("LLM explanation missing required keys, using fallback")
            if is_followup:
                return _followup_template(simulation_result, student_input)
            return _template_fallback(simulation_result)
        return explanation
    except Exception:
        logger.warning("Explanation LLM failed, using fallback", exc_info=True)
        if is_followup:
            return _followup_template(simulation_result, student_input)
        return _template_fallback(simulation_result)
