# Run Instructions

This project has a **FastAPI backend** and a **React + Vite frontend**.

## 1) Prerequisites

- Python **3.11+**
- Node.js **18+**
- npm (comes with Node)
- (Optional) Ollama for local/offline LLM mode

## 2) Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

Update `backend/.env` as needed:

- `LLM_MODE=claude` (requires `ANTHROPIC_API_KEY`)
- `LLM_MODE=ollama` (requires local Ollama running)
- `LLM_MODE=offline` (fully local fallback behavior)

Start backend:

```bash
uvicorn main:app --reload --port 8000
```

Backend will run at `http://localhost:8000`.

## 3) Frontend Setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at `http://localhost:3000`.

## 4) Quick Health Checks

- Open `http://localhost:3000` in browser
- Check backend status:

```bash
curl http://localhost:8000/api/status
```

- Try experiment endpoint:

```bash
curl -X POST http://localhost:8000/api/experiment \
  -H "Content-Type: application/json" \
  -d '{"user_input":"Add magnesium ribbon to dilute hydrochloric acid"}'
```

## 5) Offline Mode (Optional)

If using Ollama:

```bash
ollama pull phi3:mini
```

Then set in `backend/.env`:

```env
LLM_MODE=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
```

If you want no external LLM dependency at all, use:

```env
LLM_MODE=offline
```

## 6) Troubleshooting

- **CORS issue in browser**: Ensure `CORS_ORIGINS` in `backend/.env` includes `http://localhost:3000`
- **LLM errors**: Switch to `LLM_MODE=offline` to continue demoing core reaction flow
- **Port conflict**: Change frontend/backend ports and update API base URL accordingly
