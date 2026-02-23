from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, HTTPException

from core.explanation_engine import generate_explanation
from core.nlp_parser import parse_experiment
from core.safety_filter import check_safety
from core.simulation_engine import REACTIONS_DB, simulate
from core.visualization_mapper import get_visualization
from models.request_models import ExperimentRequest
from models.response_models import ExperimentResponse, StatusResponse

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/experiment", response_model=ExperimentResponse)
async def run_experiment(payload: ExperimentRequest) -> dict[str, Any]:
    # Critical rule: safety filter runs before NLP parsing on every request.
    safety_result = check_safety(payload.user_input)
    if not safety_result["is_safe"]:
        return {
            "status": "blocked",
            "is_blocked": True,
            "safety": {
                "reason": safety_result["reason"],
                "educational_note": safety_result["educational_note"],
                "severity": safety_result["severity"],
            },
        }

    parsed = await parse_experiment(payload.user_input)
    reactants = parsed.get("reactants", [])
    if not reactants:
        raise HTTPException(status_code=400, detail={"error": "Could not understand input"})

    simulation_result = simulate(parsed)
    if not simulation_result.get("found"):
        return {
            "status": "unknown",
            "is_unknown": True,
            "message": "This reaction isn't in our database yet.",
            "partial_info": simulation_result.get("partial_info", {}),
        }

    visualization = get_visualization(simulation_result)
    explanation = await generate_explanation(
        simulation_result=simulation_result,
        student_input=payload.user_input,
        difficulty_level=simulation_result.get("difficulty_level", "class_10"),
    )

    return {
        "status": "success",
        "is_blocked": False,
        "is_unknown": False,
        "simulation": {
            "reaction_id": simulation_result.get("reaction_id"),
            "balanced_equation": simulation_result.get("balanced_equation"),
            "reactants": simulation_result.get("reactants", []),
            "products": simulation_result.get("products", []),
            "observations": simulation_result.get("observations", []),
            "thermodynamics": simulation_result.get("thermodynamics"),
        },
        "visualization": {
            "animation_asset": visualization.get("animation_asset"),
            "show_thermometer": visualization.get("show_thermometer"),
            "thermometer_direction": visualization.get("thermometer_direction"),
            "intensity": visualization.get("intensity"),
            "color_overlay": visualization.get("color_overlay"),
        },
        "explanation": explanation,
        "parsed_input": {
            "reactants": parsed.get("reactants", []),
            "action": parsed.get("action"),
            "conditions": parsed.get("conditions", {}),
            **({"parsed_by": parsed["parsed_by"]} if "parsed_by" in parsed else {}),
        },
    }


@router.get("/status", response_model=StatusResponse)
async def get_status() -> dict[str, Any]:
    return {
        "status": "ok",
        "llm_mode": os.getenv("LLM_MODE", "offline").lower(),
        "reactions_loaded": len(REACTIONS_DB),
        "version": "1.0.0",
    }


@router.get("/reactions")
async def list_reactions() -> list[dict[str, Any]]:
    return [
        {
            "id": reaction_id,
            "reactants": reaction.get("reactants", []),
            "type": reaction.get("type"),
            "difficulty_level": reaction.get("difficulty_level"),
        }
        for reaction_id, reaction in REACTIONS_DB.items()
    ]
