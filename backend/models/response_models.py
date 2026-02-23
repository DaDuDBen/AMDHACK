from pydantic import BaseModel, ConfigDict
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class SafetyPayload(BaseModel):
    reason: str
    educational_note: str
    severity: str

    model_config = ConfigDict(extra="forbid")


class SimulationPayload(BaseModel):
    reaction_id: str
    balanced_equation: str
    reactants: list[str]
    products: list[str]
    observations: list[str]
    thermodynamics: str

    model_config = ConfigDict(extra="forbid")


class VisualizationPayload(BaseModel):
    animation_asset: str
    show_thermometer: bool
    thermometer_direction: str
    intensity: str

    model_config = ConfigDict(extra="forbid")


class ExplanationPayload(BaseModel):
    what_happened: str
    socratic_question: str
    key_concept: str
    ncert_reference: str
    fun_fact: str

    model_config = ConfigDict(extra="forbid")


class SuccessResponse(BaseModel):
    status: str = "success"
    is_blocked: bool = False
    is_unknown: bool = False
    simulation: SimulationPayload
    visualization: VisualizationPayload
    explanation: ExplanationPayload
    parsed_input: dict

    model_config = ConfigDict(extra="forbid")


class BlockedResponse(BaseModel):
    status: str = "blocked"
    is_blocked: bool = True
    safety: SafetyPayload

    model_config = ConfigDict(extra="forbid")


class UnknownResponse(BaseModel):
    status: str = "unknown"
    is_unknown: bool = True
    message: str
    partial_info: dict

    model_config = ConfigDict(extra="forbid")


class StatusResponse(BaseModel):
    status: str = "ok"
    llm_mode: str
    reactions_loaded: int
    version: str = "1.0.0"

    model_config = ConfigDict(extra="forbid")


class ReactionSummary(BaseModel):
    id: str
    reactants: list[str]
    type: str
    difficulty_level: str

    model_config = ConfigDict(extra="forbid")


class ReactionsResponse(BaseModel):
    reactions: list[ReactionSummary]

    model_config = ConfigDict(extra="forbid")

class ExperimentResponse(BaseModel):
    status: str
    is_blocked: bool | None = None
    is_unknown: bool | None = None
    simulation: dict[str, Any] | None = None
    visualization: dict[str, Any] | None = None
    explanation: dict[str, Any] | None = None
    parsed_input: dict[str, Any] | None = None
    safety: SafetyPayload | None = None
    message: str | None = None
    partial_info: dict[str, Any] | None = None
