from pydantic import BaseModel, ConfigDict


class ExperimentRequest(BaseModel):
    user_input: str
    session_id: str | None = None

    model_config = ConfigDict(extra="forbid")
