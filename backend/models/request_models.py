from pydantic import BaseModel, Field


class ExperimentRequest(BaseModel):
    user_input: str = Field(min_length=1)
    session_id: str | None = None
