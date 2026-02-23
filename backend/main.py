from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from core.safety_filter import configure_safety_rules
from core.simulation_engine import configure_reactions_db

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


reactions = _load_json(DATA_DIR / "reactions.json")
safety_rules = _load_json(DATA_DIR / "safety_blocklist.json")

configure_reactions_db(reactions)
configure_safety_rules(safety_rules)

app = FastAPI(title="Prayog-Shala API", version="1.0.0")

cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
