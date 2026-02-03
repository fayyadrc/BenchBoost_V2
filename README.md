# BenchBoost_V2
Enhanced, better planned FPL assistant

Codebase Review & Improvements

1. Backend Architecture (backend/)

Current State:
middleware/api.py is the actual API entry point, while main.py appears to be a legacy CLI or divergent entry point.
Blocking Operations: The agent and tools are synchronous. api.py wraps them in asyncio.to_thread to prevent blocking the event loop.
Tooling: agent/tools.py has a comprehensive suite of tools, but they are all synchronous, which limits concurrency when fetching data from external APIs or the DB.
Improvements:
Unified Entry Point: Refactor backend/main.py to be the single entry point that launches the FastAPI app (Uvicorn), unifying the startup logic (cache warming, scheduler) currently duplicated or split between main.py and middleware/api.py.
Async Tools: Convert I/O-bound tools (DB queries, API calls, scraping) to async def. This allows you to use agent.ainvoke() and native await, significantly improving throughput under load compared to threading.
Agent Dependency: The agent is currently cached in a global variable (_AGENT_CACHE) inside api.py. In FastAPI, it's better to use a Lifespan Manager or Dependency Injection (Depends) to manage the agent's lifecycle and configuration.
2. Data Pipeline & Ingestion (ingest.sh, backend/database/)

Current State:
ingest.sh is a robust wrapper around backend/database/ingest.py.
Data is loaded into MongoDB, but api.py also relies heavily on an in-memory cache module (backend/data/cache.py) for "core game data".
Improvements:
Hybrid Caching Strategy: The reliance on in-memory cache for core data (players, teams) is good for speed but makes scaling (multiple workers) hard. Consider checking if Redis or purely MongoDB with caching headers is a viable alternative for distributed deployments, or stick to memory if single-instance is sufficient.
Error Handling in Ingest: Ensure ingest.py has retry logic for network requests (FPL API is known to be flaky/rate-limited).
3. Agent & AI Logic (backend/agent/)

Current State:
Uses gemini-2.5-flash (hardcoded in agent.py).
Tools are extensive, covering stats, rules, and live data.
Memory is persisted to MongoDB (save_chat_history), which is excellent.
Improvements:
Configurable Model: Move the model name to .env (e.g., LLM_MODEL_NAME=gemini-2.5-flash) so you can easily switch to pro or updated versions without code changes.
System Prompt Management: prompt.py likely contains the system prompt. Ensure this is versioned or easily editable without redeploying logic.
4. Frontend (frontend/src/)

Current State:
Modern stack (React 19, Tailwind 4).
Clean separation of components, hooks, pages.
Improvements:
API Client: If you are using raw fetch calls in components or hooks, consider generating a typed API client (e.g., using openapi-typescript-codegen against the FastAPI openapi.json) or using TanStack Query (React Query) for caching, loading states, and automatic retries.
Environment Variables: Ensure VITE_API_URL is used for fetch requests to allow easy switching between local dev and production backends.
5. Security & Ops

Current State:
api.py handles CORS dynamically based on .env, which is good practice.
Secrets (API keys) are loaded from .env.
Improvements:
Rate Limiting: The API currently has no rate limiting. If exposed publicly, playwright scraping tools could be abused. Add slowapi or similar middleware to limit requests per IP.
Input Validation: Ensure user inputs to the agent are sanitized or limited in length to prevent context window exhaustion attacks.
Summary of Recommended Actions

Refactor main.py & api.py: Merge startup logic and define a clear application entry point.
Async Conversion: Make tools and agent invocation asynchronous for better performance.
Config Management: Externalize LLM_MODEL_NAME and other hardcoded constants.
Frontend API Layer: Adopt React Query or a typed client for robust data fetching.
Rate Limiting: Protect your expensive scraping/inference endpoints.