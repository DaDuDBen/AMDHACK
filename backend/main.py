"""FastAPI application entrypoint for Prayog-Shala backend."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import routes as api_routes

APP_VERSION = "0.1.0"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REACTIONS_FILE = DATA_DIR / "reactions.json"
SAFETY_BLOCKLIST_FILE = DATA_DIR / "safety_blocklist.json"

load_dotenv(BASE_DIR / ".env")


def _parse_cors_origins() -> list[str]:
    env_value = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    origins = [origin.strip() for origin in env_value.split(",") if origin.strip()]
    if "http://localhost:3000" not in origins:
        origins.append("http://localhost:3000")
    return origins


def _load_json_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def create_app() -> FastAPI:
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
        app.state.reactions_data = _load_json_file(REACTIONS_FILE)
        app.state.safety_blocklist_data = _load_json_file(SAFETY_BLOCKLIST_FILE)

    @app.get("/api/status")
    def get_status() -> JSONResponse:
        reactions_data = getattr(app.state, "reactions_data", None)
        has_reactions = isinstance(reactions_data, list) and len(reactions_data) > 0
        return JSONResponse(
            {
                "status": "ok",
                "llm_mode": os.getenv("LLM_MODE", "claude"),
                "reactions_loaded": has_reactions,
                "version": APP_VERSION,
            }
        )

    router = getattr(api_routes, "router", None)
    if router is not None:
        app.include_router(router, prefix="/api")

    return app


app = create_app()
