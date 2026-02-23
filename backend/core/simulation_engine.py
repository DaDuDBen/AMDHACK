"""Local chemistry simulation engine backed by reactions.json only."""

from __future__ import annotations

from typing import Any

REACTIONS_DB: dict[str, dict[str, Any]] = {}

SUBSTANCE_CATEGORY_MAP: dict[str, str] = {
    "hydrochloric acid": "acid",
    "sulphuric acid": "acid",
    "nitric acid": "acid",
    "acetic acid": "acid",
    "sodium hydroxide": "base",
    "potassium hydroxide": "base",
    "ammonia solution": "base",
    "water": "water",
    "potassium": "alkali_metal",
    "sodium": "alkali_metal",
    "lithium": "alkali_metal",
    "magnesium": "metal",
    "zinc": "metal",
    "iron": "metal",
    "aluminium": "metal",
}

REACTANT_NOTES: dict[str, str] = {
    "copper sulphate": "Blue crystalline salt, common in school labs",
    "ethanol": "Organic alcohol, flammable",
    "hydrochloric acid": "Strong mineral acid commonly used in dilute form",
    "sulphuric acid": "Strong acid and dehydrating agent",
    "nitric acid": "Strong oxidizing acid",
    "sodium hydroxide": "Strong alkali used in neutralization reactions",
    "ammonia": "Pungent basic gas used in lab demonstrations",
    "water": "Universal solvent and reaction medium",
    "potassium": "Highly reactive Group 1 metal stored under oil",
    "sodium": "Reactive Group 1 metal",
    "magnesium": "Reactive metal often used as ribbon in school labs",
    "zinc": "Moderately reactive metal used in displacement reactions",
    "iron": "Common transition metal used in displacement and corrosion examples",
    "aluminium": "Metal that reacts with alkali after oxide layer removal",
}

CATEGORY_FALLBACKS: dict[tuple[str, ...], dict[str, Any]] = {
    tuple(sorted(("acid", "base"))): {
        "reaction_id": "template_neutralization",
        "products": ["salt", "water"],
        "balanced_equation": "Acid + Base → Salt + Water",
        "type": "neutralization",
        "observations": ["temperature may rise", "pH moves toward neutral"],
        "thermodynamics": "exothermic",
        "gas_produced": None,
        "color_change": None,
        "precipitate": None,
        "animation_type": "heat_only",
        "difficulty_level": "class_10",
        "ncert_reference": "Class 10, Chapter 2: Acids, Bases and Salts",
    },
    tuple(sorted(("acid", "metal"))): {
        "reaction_id": "template_metal_acid",
        "products": ["salt", "hydrogen gas"],
        "balanced_equation": "Metal + Acid → Salt + H₂↑",
        "type": "single_displacement",
        "observations": ["effervescence", "metal surface gradually dissolves"],
        "thermodynamics": "exothermic",
        "gas_produced": "hydrogen",
        "color_change": None,
        "precipitate": None,
        "animation_type": "bubbles",
        "difficulty_level": "class_10",
        "ncert_reference": "Class 10, Chapter 1: Chemical Reactions and Equations",
    },
    tuple(sorted(("alkali_metal", "water"))): {
        "reaction_id": "template_alkali_water",
        "products": ["metal hydroxide", "hydrogen gas"],
        "balanced_equation": "2M + 2H₂O → 2MOH + H₂↑",
        "type": "single_displacement",
        "observations": ["vigorous bubbling", "heat and possible ignition"],
        "thermodynamics": "strongly_exothermic",
        "gas_produced": "hydrogen",
        "color_change": None,
        "precipitate": None,
        "animation_type": "reactive_bubbles",
        "difficulty_level": "class_10",
        "ncert_reference": "Class 10, Chapter 1: Chemical Reactions and Equations",
    },
}


def configure_reactions_db(reactions_db: dict[str, dict[str, Any]]) -> None:
    """Configure the in-memory reactions database."""
    global REACTIONS_DB
    REACTIONS_DB = reactions_db


def _normalize_reactants(reactants: list[str]) -> list[str]:
    return sorted({reactant.strip().lower() for reactant in reactants if reactant and reactant.strip()})


def _build_partial_info(reactants: list[str]) -> dict[str, Any]:
    notes = {
        reactant: REACTANT_NOTES.get(reactant, "No local note available yet")
        for reactant in reactants
    }
    return {"reactant_notes": notes}


def simulate(parsed_experiment: dict[str, Any]) -> dict[str, Any]:
    """Simulate reaction from parsed input using local lookup only."""
    normalized = _normalize_reactants(parsed_experiment.get("reactants", []))
    reactants_key = "|".join(normalized)

    for reaction_id, reaction in REACTIONS_DB.items():
        if reaction.get("reactants_key") == reactants_key:
            return {
                "found": True,
                "reaction_id": reaction_id,
                **reaction,
            }

    categories = tuple(sorted(SUBSTANCE_CATEGORY_MAP.get(reactant, "unknown") for reactant in normalized))
    if "unknown" not in categories and categories in CATEGORY_FALLBACKS:
        template = CATEGORY_FALLBACKS[categories]
        return {
            "found": True,
            "reactants": normalized,
            **template,
        }

    return {
        "found": False,
        "partial_info": _build_partial_info(normalized),
    }
