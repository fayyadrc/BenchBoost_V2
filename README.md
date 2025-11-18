# BenchBoost_V2
Enhanced, better planned FPL assistant

## Run Instructions

- Backend (FastAPI middleware):
	- Ensure `GOOGLE_API_KEY` is set in your shell; the agent uses Google Generative AI.
	- Optional: set `FRONTEND_URLS` (comma-separated) for CORS in production.

```zsh
export GOOGLE_API_KEY="<your_api_key>"
# optional for production deployments
export FRONTEND_URLS="http://localhost:5173,http://127.0.0.1:5173"

pip install -r requirements.txt
uvicorn backend.middleware.api:app --reload --host 0.0.0.0 --port 8000
```

- Frontend (Vite + React):
	- The dev server proxies `/api` to `http://localhost:8000`.

```zsh
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. Ask a question; the app posts to `/api/query` and displays the agent's response. Sessions persist via a client-side `session_id` stored in `localStorage`.
