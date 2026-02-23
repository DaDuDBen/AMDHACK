# AGENTS.md — Prayog-Shala

## Project Overview
Offline-capable AI virtual chemistry lab. Full spec is in README.md. 
Read README.md entirely before starting any task.

## Critical Execution Rules (never violate these)
1. The safety filter (`safety_filter.py`) MUST run before the NLP parser on every 
   /api/experiment request. No exceptions.
2. The simulation engine MUST be 100% local — it reads reactions.json only, never calls an LLM.
3. LLM_MODE env var must cleanly switch behaviour: "claude" | "ollama" | "offline"
4. All API response shapes must exactly match the JSON contracts in README.md API Reference.
5. Use the system prompt text from README.md Module Specifications verbatim — do not rewrite them.

## Implementation Order (respect this for dependency reasons)
scaffold → reactions.json → safety_blocklist.json → safety_filter.py → 
simulation_engine.py → visualization_mapper.py → nlp_parser.py → 
explanation_engine.py → models → routes → main.py → frontend

## How to Verify Your Work
- After scaffold: run `find . -type f | sort` and compare to Project Structure in README
- After reactions.json: confirm all 25 reactions from the table are present with correct schema
- After backend modules: run `uvicorn main:app` from backend/ — server must start with 0 errors
- After routes: test the 3 demo script inputs from README manually or with curl
- After frontend: `npm run dev` must start with 0 errors and the chat input must be functional

## Stack Versions
- Python 3.11, FastAPI, Pydantic v2, Anthropic SDK latest
- Node 18, React 18, Vite 5, TailwindCSS 3
- Do not introduce dependencies not in requirements.txt without good reason

## File Locations
- All env config via backend/.env (copy from .env.example)
- All chemistry data in backend/data/ as JSON — never hardcoded in Python
- All animation assets in frontend/src/assets/animations/ as .json files

## Verification Method
The Codex sandbox has no outbound network access. Do NOT attempt pip install 
or uvicorn server start to verify work. Instead verify by:
- Static import check: `python3 -c "import ast; ast.parse(open('main.py').read())"` 
  for each .py file
- Schema check: `python3 -c "import json; json.load(open('data/reactions.json'))"` 
  for data files
- Confirm all imports in a file resolve to files that exist in the repo
```

---

## What You Should Do Right Now

**Don't re-run the verification in Codex.** Instead, pull the repo to your local machine and run the smoke test there yourself. That's the right place to do it — Codex writes the code, you run it locally.

Once it passes locally, give Codex the green light for Plan B with this prompt:
```
Backend has been verified locally — server starts and all 3 smoke test 
curl commands pass. Proceed with Plan B frontend implementation. 
Do not attempt pip install or server startup to verify — use static 
analysis only (ast.parse for Python, json.load for data files).
