# Changelog — Prayog-Shala

All notable changes for the hackathon MVP push are documented here.

---

## [Unreleased] — Phase 1: Backend LLM & Core Fixes

_Started: 2026-04-03_

### Bugfixes
- **Follow-up questions now work from frontend** — Two bugs: (1) regex fallback hardcoded `action="mix"` even when no action keyword found, so follow-up detection never triggered; (2) route condition `not action` was always False. Fixed: action defaults to `None` in regex fallback, route now checks `not reactants and payload.context` only.

### Added
- `backend/.env` — Groq as default LLM (`llama-3.3-70b-versatile`), chemistry-mistral-7b for Ollama
- `backend/api/__init__.py`, `backend/core/__init__.py`, `backend/models/__init__.py` — proper Python package init files
- **Follow-up question support** — `/api/experiment` now accepts optional `context` field. When no reactants are detected but context exists, routes to explanation engine as a follow-up (enables "Why does the test tube feel warm?" in demo)
- **`POST /api/mode`** endpoint — switch LLM mode at runtime for live demo (groq ↔ ollama ↔ offline)
- **`switchMode()`** in `frontend/src/utils/api.js` — frontend API call for mode switching
- **Follow-up context tracking** in `useExperiment.js` — automatically passes last simulation result as context
- **Reaction-type-specific template fallbacks** in explanation engine — 10 distinct templates (single_displacement, combustion, precipitation, etc.) instead of 1 generic
- **Follow-up question templates** — pattern-matched answers for common follow-ups (heat, bubbles, color)
- **40+ chemical name aliases** in NLP parser — magnesium ribbon, iron nail, baking soda, vinegar, HCl, CaCO3, etc.

### Changed
- `backend/.env.example` — now shows Groq as recommended default, chemistry-mistral-7b for Ollama
- `nlp_parser.py` — Ollama timeout 10s → 60s, model default `phi3:mini` → `chemistry-mistral-7b`, lazy SDK imports, markdown fence stripping, post-LLM reactant normalization, logging
- `explanation_engine.py` — Ollama timeout 60s, lazy imports, improved fallback quality, `is_followup` parameter
- `main.py` — removed duplicate `/api/status` endpoint (now only in routes.py), added startup logging, wider CORS origins
- `routes.py` — added follow-up detection (step 4 in pipeline), mode switch route, proper logging
- `request_models.py` — added optional `context: dict | None` field
- `StatusIndicator.jsx` — now shows all 4 modes: Claude (green), Groq (green), Ollama/Local (amber), Offline (grey) with animated pulse dot
- `useExperiment.js` — tracks last simulation via ref, passes as context
- `api.js` — `runExperiment()` accepts context param, added `switchMode()` function

### Removed
- Duplicate reaction `cu_agno3_039` (same reactants_key as `cu_agno3_010`)
- Duplicate reaction `mg_hcl_040` (same reactants_key as `mg_hcl_001`)
- Duplicate `/api/status` handler in `main.py` (kept the one in `routes.py`)

### Verified
- All 9 Python files pass `ast.parse()` syntax check ✅
- `reactions.json`: 66 reactions, valid JSON ✅
- `safety_blocklist.json`: 15 rules, valid JSON ✅
