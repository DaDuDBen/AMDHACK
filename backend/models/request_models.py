from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ExperimentRequest(BaseModel):
    user_input: str = Field(..., min_length=1, max_length=500)
    session_id: str | None = None
    context: dict[str, Any] | None = None  # Previous simulation result for follow-up questions

    model_config = ConfigDict(extra="forbid")
