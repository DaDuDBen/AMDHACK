# 🧪 Prayog-Shala — The Generative Virtual Science Lab

> **Hackathon Project | Theme: Bridging the Digital Divide**
> An offline-capable, AI-powered virtual chemistry lab for students in Tier-2/3 cities and rural India who have never had access to a real science laboratory.

---

## 📌 Table of Contents

- [Project Vision](#-project-vision)
- [Live Demo Flow](#-live-demo-flow)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Module Specifications](#-module-specifications)
  - [1. Frontend UI](#1-frontend-ui)
  - [2. Backend API Server](#2-backend-api-server)
  - [3. NLP Parser (LLM Layer)](#3-nlp-parser-llm-layer)
  - [4. Chemistry Simulation Engine](#4-chemistry-simulation-engine)
  - [5. Safety Filter](#5-safety-filter)
  - [6. Visualization Layer](#6-visualization-layer)
  - [7. Explanation Engine (Socratic Layer)](#7-explanation-engine-socratic-layer)
- [Database Schema](#-database-schema)
- [API Reference](#-api-reference)
- [Environment Variables](#-environment-variables)
- [Setup & Running Locally](#-setup--running-locally)
- [Offline Mode](#-offline-mode)
- [Error Handling Spec](#-error-handling-spec)
- [Demo Script (for judges)](#-demo-script-for-judges)
- [Future Roadmap](#-future-roadmap)

---

## 🌟 Project Vision

Millions of Indian students study chemistry and physics from textbooks but graduate without ever performing a real experiment. Schools in Chhattisgarh, Bihar, and rural Rajasthan often have labs that exist on paper — locked rooms with broken equipment and no reagents.

**Prayog-Shala** (Hindi: *Laboratory*) is a virtual science lab that runs entirely on a school-issued laptop — no internet required after initial setup. A student types a natural language command like _"Mix hydrochloric acid with zinc"_ and the system:

1. Parses the instruction using an on-device language model
2. Looks up the reaction in a local chemistry knowledge base
3. Validates safety constraints
4. Returns a visual simulation + a Socratic explanation that teaches the *why*

The system is built to run on **AMD Ryzen AI laptops** (using the NPU for inference) but also works on any standard CPU-based machine via Ollama.

---

## 🎬 Live Demo Flow

The intended demo for judges is this exact sequence:

1. Student opens the app in a browser (`localhost:3000`)
2. Types: **"Add a piece of magnesium ribbon to dilute hydrochloric acid"**
3. System shows:
   - ✅ A bubble animation (hydrogen gas being released)
   - 🧪 The balanced equation: `Mg + 2HCl → MgCl₂ + H₂↑`
   - 🌡️ An indicator showing heat is produced (exothermic)
   - 📖 A Socratic explanation: _"What do you think the bubbles are made of? Why do you think the test tube feels warm?"_
4. Student types: **"What happens if I add more acid?"**
5. System explains the limiting reagent concept
6. Student types: **"Mix potassium with water"**
7. Safety layer intercepts → shows educational warning card about alkali metal reactivity

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER (React UI)                       │
│   [Chat Input] ──────────────────────► [Visualization Panel]   │
│   [Experiment History]                  [Equation Display]      │
│   [Safety Warning Modal]                [Explanation Card]      │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP POST /api/experiment
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (Python)                      │
│                                                                  │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────────────┐ │
│  │ Safety      │──►│ NLP Parser   │──►│ Simulation Engine    │ │
│  │ Filter      │   │ (LLM Layer)  │   │ (Rules DB + Logic)   │ │
│  └─────────────┘   └──────────────┘   └──────────────────────┘ │
│                           │                       │             │
│                           ▼                       ▼             │
│                   ┌──────────────┐   ┌──────────────────────┐  │
│                   │ Explanation  │   │ Visualization        │  │
│                   │ Engine       │   │ Selector             │  │
│                   └──────────────┘   └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐     ┌──────────────────────┐
│  reactions.json  │     │  LLM (Ollama /        │
│  (local rules DB)│     │  Claude API fallback) │
└──────────────────┘     └──────────────────────┘
```

**Key design principle:** The simulation engine and safety filter are **100% local and offline** — they use a JSON rules database, not the LLM. The LLM is only used for (a) parsing natural language and (b) generating explanations. This means the core functionality works even if the LLM is unavailable.

---

## 🛠️ Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Frontend | React + Vite + TailwindCSS | Fast to build, clean UI |
| Animations | Lottie (JSON animations) + CSS | Lightweight, offline-safe |
| Backend | Python 3.11 + FastAPI | Async, clean API design |
| LLM (online mode) | Claude API (`claude-sonnet-4-6`) | High-quality parsing & explanation |
| LLM (offline mode) | Ollama + `phi3:mini` | Runs on CPU/NPU locally |
| Chemistry DB | JSON flat file (`reactions.json`) | Zero dependencies, fully offline |
| Safety Filter | Python rule engine (no LLM) | Deterministic, cannot be bypassed |
| Package Manager | `uv` (Python) + `npm` (Node) | Speed |

---

## 📁 Project Structure

```
prayog-shala/
│
├── README.md                        # This file
├── .env.example                     # Environment variable template
├── .gitignore
│
├── backend/
│   ├── main.py                      # FastAPI app entry point
│   ├── requirements.txt
│   │
│   ├── api/
│   │   └── routes.py                # All API route definitions
│   │
│   ├── core/
│   │   ├── safety_filter.py         # Safety check logic (no LLM)
│   │   ├── nlp_parser.py            # LLM call to parse user input → structured JSON
│   │   ├── simulation_engine.py     # Core reaction lookup + calculation logic
│   │   ├── explanation_engine.py    # LLM call to generate Socratic explanation
│   │   └── visualization_mapper.py  # Maps reaction type → animation asset name
│   │
│   ├── data/
│   │   ├── reactions.json           # Full chemistry rules database
│   │   └── safety_blocklist.json   # Forbidden/dangerous combinations + warnings
│   │
│   └── models/
│       ├── request_models.py        # Pydantic models for API requests
│       └── response_models.py       # Pydantic models for API responses
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   │
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       │
│       ├── components/
│       │   ├── ChatInput.jsx         # Text input + submit button
│       │   ├── ExperimentHistory.jsx # Scrollable list of past experiments
│       │   ├── VisualizationPanel.jsx # Renders animation + equation
│       │   ├── ExplanationCard.jsx   # Socratic explanation display
│       │   ├── SafetyWarningModal.jsx # Modal for blocked experiments
│       │   └── StatusIndicator.jsx   # Online/offline mode badge
│       │
│       ├── assets/
│       │   └── animations/           # Lottie JSON files for each reaction type
│       │       ├── bubbles.json
│       │       ├── fire.json
│       │       ├── color_change.json
│       │       ├── precipitate.json
│       │       ├── smoke.json
│       │       └── explosion_safe.json  # For the safety warning card
│       │
│       ├── hooks/
│       │   └── useExperiment.js      # Custom hook for API calls + state
│       │
│       └── utils/
│           └── api.js                # Axios config + API call wrappers
│
└── docs/
    ├── architecture.md
    └── reactions_reference.md        # Human-readable list of all supported reactions
```

---

## 📐 Module Specifications

### 1. Frontend UI

**File:** `frontend/src/App.jsx` and all components under `frontend/src/components/`

**Layout:** Two-column split screen.
- **Left panel (40% width):** Chat interface. Shows `ExperimentHistory` (scrollable list of past inputs and brief results) and `ChatInput` at the bottom.
- **Right panel (60% width):** Shows `VisualizationPanel` (animation + balanced equation + thermodynamics badge) and `ExplanationCard` (the Socratic explanation text) stacked vertically.

**Behavior:**
- On submit, set a loading state and show a spinner in the right panel.
- If the API returns `is_blocked: true`, show `SafetyWarningModal` instead of normal result.
- If the API returns `is_unknown: true`, show a graceful "Reaction not in database" message with whatever partial info is available.
- Show a small `StatusIndicator` badge in the top-right corner: green "🟢 Online (Claude)" or yellow "🟡 Offline (Phi-3)" based on which LLM mode the backend is using. The backend should expose a `/api/status` endpoint for this.
- The app must work fully if JavaScript animations fail to load (graceful degradation: show equation and text only).

**Styling:** Use TailwindCSS. Color theme: deep navy (`#0f172a`) background, white cards, accent color teal (`#14b8a6`). The lab aesthetic — clean, scientific, not childish.

---

### 2. Backend API Server

**File:** `backend/main.py`

Build a FastAPI application. Configure CORS to allow requests from `localhost:3000`. Mount the main router from `api/routes.py`.

On startup, load `reactions.json` and `safety_blocklist.json` into memory as module-level dictionaries so they aren't read from disk on every request.

Include a health check endpoint at `GET /api/status` that returns:
```json
{
  "status": "ok",
  "llm_mode": "claude" | "ollama" | "offline",
  "reactions_loaded": 32,
  "version": "1.0.0"
}
```

---

### 3. NLP Parser (LLM Layer)

**File:** `backend/core/nlp_parser.py`

**Purpose:** Convert a free-text student instruction into a structured JSON object the simulation engine can process.

**Function signature:**
```python
async def parse_experiment(user_input: str) -> dict:
    """
    Returns:
    {
        "reactants": ["magnesium", "hydrochloric acid"],
        "action": "mix",          # mix | heat | dissolve | burn | add_to
        "conditions": {
            "temperature": "room",  # room | heated | cooled
            "concentration": "dilute" | "concentrated" | null,
            "quantity_notes": "small piece" | null
        },
        "raw_input": "original user text"
    }
    """
```

**LLM Prompt (system prompt for the LLM call):**
```
You are a chemistry lab assistant that parses student experiment instructions into structured JSON.
Extract the reactants, action, and conditions from the student's input.
Normalize chemical names to their common IUPAC or textbook names (e.g., "muriatic acid" → "hydrochloric acid", "lye" → "sodium hydroxide").
Always return ONLY valid JSON. No explanation, no markdown, no preamble.
```

**Fallback behavior:** If the LLM call fails (network error, timeout), attempt a simple regex-based extraction. Extract capitalized nouns as reactants and common verbs (mix, add, heat, burn) as the action. Return a best-effort dict with a flag `"parsed_by": "fallback_regex"`.

**LLM provider switching:** Check for environment variable `LLM_MODE`.
- If `LLM_MODE=claude`: use Anthropic SDK, model `claude-sonnet-4-6`
- If `LLM_MODE=ollama`: use `httpx` to POST to `http://localhost:11434/api/generate`, model `phi3:mini`
- If `LLM_MODE=offline`: skip LLM entirely, use fallback regex only

---

### 4. Chemistry Simulation Engine

**File:** `backend/core/simulation_engine.py`

**Purpose:** The core "physics" of the app. Given a parsed experiment dict, look up the matching reaction and return its properties.

**Function signature:**
```python
def simulate(parsed_experiment: dict) -> dict:
    """
    Returns:
    {
        "found": true,
        "reaction_id": "mg_hcl_001",
        "reactants": ["magnesium", "hydrochloric acid"],
        "products": ["magnesium chloride", "hydrogen gas"],
        "balanced_equation": "Mg + 2HCl → MgCl₂ + H₂↑",
        "type": "single_displacement",
        "observations": ["effervescence", "solid dissolves", "heat produced"],
        "thermodynamics": "exothermic",
        "gas_produced": "hydrogen",
        "color_change": null,
        "precipitate": null,
        "animation_type": "bubbles_with_heat",
        "difficulty_level": "class_10",
        "ncert_reference": "Chapter 1, Chemical Reactions and Equations"
    }
    """
```

**Lookup logic:**
1. Normalize all reactant names to lowercase
2. Sort reactant list alphabetically (so "zinc + acid" and "acid + zinc" both match)
3. Check `reactions.json` for a match on the `reactants_key` field (which is the sorted, joined reactant list, e.g., `"hydrochloric acid|magnesium"`)
4. If no exact match, try matching on individual reactant categories (e.g., "any acid" + "any alkali metal" → neutralization template)
5. If no match at all, return `{"found": false, "partial_info": {...}}` with whatever is known about each individual reactant

---

### 5. Safety Filter

**File:** `backend/core/safety_filter.py`

**Purpose:** Run BEFORE the NLP parser. Deterministically block dangerous experiment requests using a rules-based system — never the LLM, which could be fooled.

**Function signature:**
```python
def check_safety(user_input: str) -> dict:
    """
    Returns:
    {
        "is_safe": true | false,
        "reason": null | "string explaining why it's blocked",
        "educational_note": null | "string with safe educational context",
        "severity": null | "warning" | "danger"
    }
    """
```

**Rules to implement (load from `safety_blocklist.json`):**
The blocklist JSON should be an array of rule objects, each with:
- `keywords`: list of trigger keywords (check if all keywords in a rule appear in the lowercased input)
- `reason`: human-readable block reason
- `educational_note`: what to teach the student instead
- `severity`: `"warning"` or `"danger"`

**Minimum blocklist entries to include:**
```json
[
  {
    "keywords": ["potassium", "water"],
    "reason": "Alkali metals react violently with water",
    "educational_note": "Potassium reacts explosively with water, releasing hydrogen gas and enough heat to ignite it. This reaction is studied theoretically at school level for safety reasons. Group 1 metals become increasingly reactive down the period.",
    "severity": "warning"
  },
  {
    "keywords": ["sodium", "water"],
    "reason": "Alkali metal + water reaction",
    "educational_note": "Sodium reacts vigorously with water. In a real lab, this must be performed in a fume cupboard using tiny quantities. The reaction produces sodium hydroxide and hydrogen gas.",
    "severity": "warning"
  },
  {
    "keywords": ["thermite"],
    "reason": "Thermite is an incendiary mixture",
    "educational_note": "Thermite is a mixture of aluminium powder and iron oxide that burns at extremely high temperatures. It's used industrially for welding railway lines. It is not a school-level experiment.",
    "severity": "danger"
  },
  {
    "keywords": ["chlorine", "ammonia"],
    "reason": "Produces toxic chloramine gases",
    "educational_note": "Mixing chlorine-based compounds with ammonia-based compounds produces toxic chloramine vapors. This is why you should never mix bleach with ammonia-based cleaners at home.",
    "severity": "danger"
  },
  {
    "keywords": ["concentrated", "nitric acid", "glycerol"],
    "reason": "Explosive compound precursor",
    "educational_note": "This combination can produce nitroglycerin, a powerful and unstable explosive. This is strictly industrial/controlled chemistry.",
    "severity": "danger"
  }
]
```

Add at least 10 more rules covering common dangerous school chemistry mistakes.

---

### 6. Visualization Layer

**File:** `backend/core/visualization_mapper.py`

**Purpose:** Map a simulation result's `animation_type` field to the correct frontend animation asset filename.

**Function signature:**
```python
def get_visualization(simulation_result: dict) -> dict:
    """
    Returns:
    {
        "animation_asset": "bubbles.json",  # filename in frontend/src/assets/animations/
        "color_overlay": null | "#hex_color",  # for color change reactions
        "intensity": "low" | "medium" | "high",  # controls animation speed
        "show_thermometer": true | false,
        "thermometer_direction": "up" | "down" | null
    }
    """
```

**Animation type mapping table to implement:**

| `animation_type` | `animation_asset` | Notes |
|---|---|---|
| `bubbles` | `bubbles.json` | Gas produced, no significant heat |
| `bubbles_with_heat` | `bubbles.json` + thermometer up | Exothermic + gas |
| `fire` | `fire.json` | Combustion reactions |
| `color_change_blue` | `color_change.json` | e.g., litmus in acid |
| `color_change_red` | `color_change.json` | e.g., litmus in base |
| `precipitate_white` | `precipitate.json` | White solid forms |
| `precipitate_yellow` | `precipitate.json` | Yellow solid |
| `smoke` | `smoke.json` | Solid + solid reaction with fumes |
| `dissolve` | `dissolve.json` | Solid dissolves cleanly |
| `no_reaction` | `no_reaction.json` | Noble gases, etc. |

---

### 7. Explanation Engine (Socratic Layer)

**File:** `backend/core/explanation_engine.py`

**Purpose:** Generate a pedagogically valuable explanation of the reaction. The key design goal is **Socratic** — guide the student to the answer through questions rather than just dumping facts.

**Function signature:**
```python
async def generate_explanation(
    simulation_result: dict,
    student_input: str,
    difficulty_level: str = "class_10"
) -> dict:
    """
    Returns:
    {
        "what_happened": "Short 1-2 sentence plain English description",
        "socratic_question": "A guiding question to prompt further thinking",
        "key_concept": "The core chemistry concept this reaction illustrates",
        "ncert_reference": "Chapter X, Topic Y",
        "fun_fact": "An interesting real-world application of this reaction"
    }
    """
```

**LLM System Prompt:**
```
You are Prayog, a friendly chemistry tutor for Indian school students (Class 8-12).
You explain reactions clearly and simply, using examples from everyday Indian life where possible.
You follow the Socratic method — after explaining what happened, always ask one guiding question
that makes the student think deeper about WHY it happened.
Keep explanations under 100 words. Use simple English.
Reference NCERT chapters when relevant.
Always return ONLY valid JSON with keys: what_happened, socratic_question, key_concept, ncert_reference, fun_fact.
```

**Example output for Mg + HCl:**
```json
{
  "what_happened": "The magnesium metal displaced hydrogen from the acid, forming magnesium chloride salt and hydrogen gas — which is why you see bubbles.",
  "socratic_question": "If we used zinc instead of magnesium, do you think the reaction would be faster or slower? Why?",
  "key_concept": "Single Displacement Reaction & Reactivity Series",
  "ncert_reference": "Class 10, Chapter 1: Chemical Reactions and Equations",
  "fun_fact": "This reaction is used in some portable hydrogen generators for weather balloons!"
}
```

---

## 🗄️ Database Schema

### `backend/data/reactions.json`

The file is a JSON object where each key is the reaction ID and value is the reaction data.

```json
{
  "mg_hcl_001": {
    "reactants_key": "hydrochloric acid|magnesium",
    "reactants": ["magnesium", "hydrochloric acid"],
    "products": ["magnesium chloride", "hydrogen gas"],
    "balanced_equation": "Mg + 2HCl → MgCl₂ + H₂↑",
    "type": "single_displacement",
    "observations": ["effervescence", "solid dissolves", "mild heat"],
    "thermodynamics": "exothermic",
    "gas_produced": "hydrogen",
    "color_change": null,
    "precipitate": null,
    "animation_type": "bubbles_with_heat",
    "difficulty_level": "class_10",
    "ncert_reference": "Class 10, Chapter 1"
  }
}
```

**Implement at minimum the following 25 reactions:**

| # | Reactants | Type | Class Level |
|---|---|---|---|
| 1 | Magnesium + Hydrochloric Acid | Single displacement | Class 10 |
| 2 | Zinc + Sulphuric Acid | Single displacement | Class 10 |
| 3 | Iron + Copper Sulphate solution | Single displacement | Class 10 |
| 4 | Sodium Hydroxide + Hydrochloric Acid | Neutralization | Class 10 |
| 5 | Calcium Carbonate + Hydrochloric Acid | Double displacement | Class 10 |
| 6 | Magnesium + Oxygen (burning) | Combination / Combustion | Class 10 |
| 7 | Hydrogen + Oxygen | Combination | Class 10 |
| 8 | Silver Nitrate + Sodium Chloride | Precipitation | Class 10 |
| 9 | Lead Nitrate + Potassium Iodide | Precipitation | Class 10 |
| 10 | Copper + Silver Nitrate | Single displacement | Class 10 |
| 11 | Barium Chloride + Sulphuric Acid | Double displacement | Class 10 |
| 12 | Carbon + Oxygen | Combustion | Class 9 |
| 13 | Methane + Oxygen | Combustion | Class 11 |
| 14 | Litmus + Acid | Indicator test | Class 7 |
| 15 | Litmus + Base | Indicator test | Class 7 |
| 16 | Copper + Heat | Decomposition | Class 10 |
| 17 | Ferrous Sulphate + Heat | Decomposition | Class 10 |
| 18 | Calcium Oxide + Water | Combination | Class 10 |
| 19 | Ammonia + Hydrochloric Acid | Combination | Class 11 |
| 20 | Zinc + Copper Sulphate | Single displacement | Class 10 |
| 21 | Iron + Hydrochloric Acid | Single displacement | Class 9 |
| 22 | Sodium Carbonate + Hydrochloric Acid | Double displacement | Class 10 |
| 23 | Hydrogen Peroxide (decomposition) | Decomposition | Class 11 |
| 24 | Aluminium + Sodium Hydroxide | Special | Class 11 |
| 25 | Universal Indicator + various pH | Indicator test | Class 11 |

---

## 🔌 API Reference

### `POST /api/experiment`

**Request body:**
```json
{
  "user_input": "Mix magnesium ribbon with dilute hydrochloric acid",
  "session_id": "optional-uuid-for-session-tracking"
}
```

**Response (success):**
```json
{
  "status": "success",
  "is_blocked": false,
  "is_unknown": false,
  "simulation": {
    "reaction_id": "mg_hcl_001",
    "balanced_equation": "Mg + 2HCl → MgCl₂ + H₂↑",
    "reactants": ["magnesium", "hydrochloric acid"],
    "products": ["magnesium chloride", "hydrogen gas"],
    "observations": ["effervescence", "solid dissolves", "mild heat"],
    "thermodynamics": "exothermic"
  },
  "visualization": {
    "animation_asset": "bubbles.json",
    "show_thermometer": true,
    "thermometer_direction": "up",
    "intensity": "medium"
  },
  "explanation": {
    "what_happened": "...",
    "socratic_question": "...",
    "key_concept": "Single Displacement Reaction",
    "ncert_reference": "Class 10, Chapter 1",
    "fun_fact": "..."
  },
  "parsed_input": {
    "reactants": ["magnesium", "hydrochloric acid"],
    "action": "mix",
    "conditions": {"concentration": "dilute"}
  }
}
```

**Response (blocked):**
```json
{
  "status": "blocked",
  "is_blocked": true,
  "safety": {
    "reason": "Alkali metals react violently with water",
    "educational_note": "...",
    "severity": "warning"
  }
}
```

**Response (unknown reaction):**
```json
{
  "status": "unknown",
  "is_unknown": true,
  "message": "This reaction isn't in our database yet.",
  "partial_info": {
    "reactant_notes": {
      "copper sulphate": "Blue crystalline salt, common in school labs",
      "ethanol": "Organic alcohol, flammable"
    }
  }
}
```

---

### `GET /api/status`

Returns server health and LLM mode (see Backend section above).

---

### `GET /api/reactions`

Returns the full list of supported reactions (id, reactants, type, difficulty_level only — no full data). Used by the frontend to optionally show a "Browse reactions" panel.

---

## ⚙️ Environment Variables

Create a `.env` file in the `backend/` directory. See `.env.example`:

```env
# LLM Mode: "claude" | "ollama" | "offline"
LLM_MODE=claude

# Required only if LLM_MODE=claude
ANTHROPIC_API_KEY=sk-ant-...

# Required only if LLM_MODE=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# Server config
PORT=8000
CORS_ORIGINS=http://localhost:3000
```

---

## 🚀 Setup & Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional for offline mode) [Ollama](https://ollama.ai) installed

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env to add your ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

### Offline Mode (Ollama)

```bash
# Install Ollama, then:
ollama pull phi3:mini

# In backend/.env:
LLM_MODE=ollama
OLLAMA_BASE_URL=http://localhost:11434

# Then run backend as normal
```

### requirements.txt (backend)

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
anthropic>=0.28.0
httpx>=0.27.0
pydantic>=2.7.0
python-dotenv>=1.0.0
```

---

## 📡 Offline Mode

The app is designed with offline-first principles:

| Feature | Online Mode | Offline Mode |
|---|---|---|
| NLP Parsing | Claude API | Phi-3 via Ollama |
| Reaction Simulation | Local JSON DB | Local JSON DB ✅ |
| Safety Filter | Local rules | Local rules ✅ |
| Explanation | Claude API | Phi-3 via Ollama |
| Animations | Local files | Local files ✅ |

In full offline mode (`LLM_MODE=offline`), the app uses the fallback regex parser and generates templated explanations from the `reactions.json` fields directly. The experience is degraded but functional.

---

## 🛡️ Error Handling Spec

Every backend module must handle these cases:

| Scenario | Behavior |
|---|---|
| LLM API timeout (>10s) | Log warning, fall back to regex parser |
| LLM returns malformed JSON | Retry once, then use fallback |
| Reaction not in DB | Return `is_unknown: true` with partial info |
| Safety rule triggered | Return `is_blocked: true` immediately, skip all other processing |
| All fields missing in parse | Return 400 with `"error": "Could not understand input"` |
| Ollama not running | Return 503 with `"error": "Offline LLM unavailable, set LLM_MODE=offline"` |

---

## 🎤 Demo Script (for judges)

Use this exact sequence when demoing to judges:

**1. Normal reaction (impressive visual)**
> _"Add magnesium ribbon to dilute hydrochloric acid"_
→ Shows bubbles animation, balanced equation, exothermic badge, Socratic question

**2. Follow-up question (shows AI understanding context)**
> _"Why does the test tube feel warm?"_
→ Explains exothermic reaction, bond energy, links to NCERT Chapter 1

**3. Safety filter (shows responsible AI)**
> _"Mix potassium with water"_
→ Shows educational warning card with the science behind why it's dangerous

**4. Unknown reaction (graceful degradation)**
> _"Dissolve copper in ethanol"_
→ Shows "not in database" with partial info about each substance

**5. Offline mode toggle (show the architecture)**
Switch `LLM_MODE=offline` and repeat experiment 1.
→ Works! Parser uses regex, explanation uses template. Core science never fails.

---

## 🔭 Future Roadmap

- **Physics module:** Inclined planes, optics, circuits using the same architecture
- **Voice input:** Whisper (on-device ASR) so students can speak their experiment
- **3D visualization:** Replace Lottie with Three.js scenes for more complex reactions
- **Mastery tracking:** Local SQLite DB that tracks which reactions a student has explored and surfaces related concepts
- **Teacher dashboard:** Aggregated (anonymous) analytics on which reactions students attempt most
- **Multilingual support:** Hindi, Tamil, Telugu UI via i18n + regional language LLM prompts
- **AMD NPU optimization:** Quantized Phi-3 running via ONNX Runtime with DirectML on Ryzen AI NPUs

---

## 👥 Team

| Role | Responsibility |
|---|---|
| Full-stack Dev | Frontend React UI + FastAPI backend |
| AI/ML Engineer | LLM integration, prompt engineering, simulation engine |
| Domain Expert | Chemistry rules database, NCERT mapping |
| Designer | UI/UX, animation assets |

---

## 📄 License

MIT License. Built for [Hackathon Name] — Theme: Bridging the Digital Divide.

---

*"Every student deserves a laboratory. Prayog-Shala makes sure geography is never the reason they don't have one."*
