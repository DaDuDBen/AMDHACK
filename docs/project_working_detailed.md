# Detailed Working of Prayog-Shala

## Overview

Prayog-Shala is an offline-capable virtual chemistry lab designed to let students type natural-language experiment instructions and receive:

- safe execution feedback,
- reaction simulation output,
- visualization metadata,
- and guided conceptual explanation.

The system is split into a **React frontend** and **FastAPI backend**, with the chemistry logic grounded in local JSON data.

---

## End-to-End Request Flow

When a user enters a prompt such as:

> "Add magnesium ribbon to dilute hydrochloric acid"

The following pipeline executes:

1. Frontend sends `POST /api/experiment` with user input.
2. Backend runs **Safety Filter first** to block dangerous requests.
3. If safe, backend runs **NLP Parser** to extract reactants/action/conditions.
4. Parsed entities are matched in **Simulation Engine** against local `reactions.json`.
5. **Visualization Mapper** chooses animation and UI indicators.
6. **Explanation Engine** generates a teaching response (Socratic style).
7. Backend returns a structured JSON response for frontend rendering.

---

## Backend Modules and Their Roles

## 1) Safety Filter

- Runs before parser/simulation.
- Uses local `safety_blocklist.json`.
- Detects dangerous combinations (e.g., alkali metal + water).
- Returns immediate blocked response with educational warning.

Why this matters:

- Prevents unsafe normalization of dangerous chemistry.
- Demonstrates responsible AI behavior in education.

## 2) NLP Parser

- Converts free-form language into structured reaction intent.
- Extracts: reactants, action, conditions.
- Supports multiple modes controlled by `LLM_MODE`:
  - `claude`
  - `ollama`
  - `groq`
  - `offline`
- Fallback parsing path keeps system functional in no-network scenarios.

## 3) Simulation Engine

- Core chemistry logic layer.
- Uses **only local** `backend/data/reactions.json`.
- Finds matching reactions and returns:
  - balanced equation,
  - products,
  - observations,
  - thermodynamics,
  - reaction type and metadata.

This makes science behavior deterministic and auditable.

## 4) Visualization Mapper

- Converts simulation outcomes to UI-ready visual cues.
- Picks animation assets (bubbles, precipitate, etc.).
- Controls thermometer direction/intensity and visual emphasis.

## 5) Explanation Engine

- Produces concept-level explanation designed for learning.
- Includes:
  - what happened,
  - key concept,
  - NCERT alignment,
  - Socratic follow-up question,
  - optional fun fact.

---

## Data-Driven Architecture

### `backend/data/reactions.json`

Contains reaction records with schema-like fields such as:

- `id`
- `reactants`
- `products`
- `balanced_equation`
- `observations`
- `thermodynamics`
- `key_concept`
- `difficulty_level`

### `backend/data/safety_blocklist.json`

Contains prohibited high-risk pairs/patterns and educational safety text.

Benefits of this approach:

- easy to extend,
- no hardcoded chemistry in route handlers,
- better maintainability for domain experts.

---

## API Contract Behavior

The backend returns distinct response types:

1. **success**: valid known reaction.
2. **blocked**: dangerous input intercepted by safety layer.
3. **unknown**: reaction not found in local database.

This contract allows the frontend to render predictable states:

- simulation card,
- warning modal/card,
- graceful "not yet supported" messaging.

---

## Frontend Behavior

Frontend responsibilities:

- Chat-like input for experiment prompts.
- Display reaction equation and products.
- Show mapped animation.
- Render explanation card with guided questions.
- Show clear safety warning UI if blocked.

The UI treats backend response shape as source of truth.

---

## Offline-First Design Principles

- Reaction logic remains local even in online mode.
- Safety logic remains local and deterministic.
- LLM is assistive for parsing/explanation, not source of chemistry truth.
- Offline mode still allows useful educational flow with reduced fluency.

This design makes the project suitable for low-connectivity regions and classroom hardware constraints.

---

## Why This Architecture Works for the Hackathon Theme

**Bridging the Digital Divide** requires reliability where internet is inconsistent.

Prayog-Shala addresses this by:

- keeping critical science and safety modules local,
- minimizing cloud dependence,
- preserving educational value in degraded/offline conditions,
- making chemistry labs accessible without physical infrastructure.
