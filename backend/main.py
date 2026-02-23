"""FastAPI application entrypoint for Prayog-Shala backend."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from core.safety_filter import configure_safety_rules
from core.simulation_engine import configure_reactions_db

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REACTIONS_FILE = DATA_DIR / "reactions.json"
SAFETY_BLOCKLIST_FILE = DATA_DIR / "safety_blocklist.json"
APP_VERSION = "1.0.0"

# Explicitly load backend/.env
load_dotenv(BASE_DIR / ".env")


def _parse_cors_origins() -> list[str]:
    env_value = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    origins = [origin.strip() for origin in env_value.split(",") if origin.strip()]
    return origins or ["http://localhost:3000"]


def _load_json_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


app = FastAPI(title="Prayog-Shala API", version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup_load_data() -> None:
    reactions_data = _load_json_file(REACTIONS_FILE)
    safety_rules = _load_json_file(SAFETY_BLOCKLIST_FILE)

    app.state.reactions_data = reactions_data
    app.state.safety_rules = safety_rules

    configure_reactions_db(reactions_data)
    configure_safety_rules(safety_rules)


@app.get("/api/status")
def get_status() -> dict[str, Any]:
    reactions_data = getattr(app.state, "reactions_data", {})
    reactions_loaded = len(reactions_data) if isinstance(reactions_data, (dict, list)) else 0

    return {
        "status": "ok",
        "llm_mode": os.getenv("LLM_MODE", "offline"),
        "reactions_loaded": reactions_loaded,
        "version": "1.0.0",
    }


app.include_router(router)
