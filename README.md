# BenchBoost_V2
Enhanced, better planned FPL assistant

## Quick Start

### Option 1: Web UI (Recommended)

Use the provided startup script to run both backend API and frontend together:

```zsh
./start.sh
```

This will:
- Start the FastAPI backend on `http://localhost:8000`
- Start the Vite frontend on `http://localhost:5173`
- Automatically proxy `/api` requests from frontend to backend

Then visit `http://localhost:5173` in your browser to use the chatbot.

### Option 2: CLI Mode

Run the chatbot directly in your terminal:

```zsh
python -m backend.main
```

This starts an interactive command-line interface for the chatbot (no web UI).

## Manual Setup

If you prefer to run servers separately:

### Backend (FastAPI middleware)

Ensure `GOOGLE_API_KEY` is set in your `.env` file or shell:

```zsh
export GOOGLE_API_KEY="<your_api_key>"
# Optional for production deployments
export FRONTEND_URLS="http://localhost:5173,http://127.0.0.1:5173"

pip install -r requirements.txt
uvicorn backend.middleware.api:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Vite + React)

The dev server proxies `/api` to `http://localhost:8000`:

```zsh
cd frontend
npm install
npm run dev
```

## How It Works

- The frontend sends queries to `/api/query` via the Vite proxy
- The backend API creates an agent session per user (tracked via `session_id` in localStorage)
- Chat history is maintained server-side for context-aware responses
- The agent uses Google Generative AI with custom FPL tools and data

