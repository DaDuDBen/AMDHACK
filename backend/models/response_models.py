from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class SafetyPayload(BaseModel):
    reason: str
    educational_note: str
    severity: str


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


class StatusResponse(BaseModel):
    status: str
    llm_mode: str
    reactions_loaded: int
    version: str
