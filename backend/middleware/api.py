import os
import asyncio
import logging
import re
from typing import Optional, List, Any, Dict, Iterable
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Use the main agent implementation
from backend.agent.agent import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from backend.data import cache

# /Users/fayyadrc/Documents/Programming/FPLChatbot_V2/fplAI/backend/middleware/api.py


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FPLChatbot Middleware")

# Startup event to load core game data
@app.on_event("startup")
async def startup_event():
    """Load core FPL data on application startup."""
    logger.info("Loading core FPL game data on startup...")
    try:
        await asyncio.to_thread(cache.load_core_game_data, force_refresh=True)
        stats = cache.get_cache_stats()
        logger.info(f"✅ Cache initialized: {stats.get('cache_size')} entries loaded")
        logger.info(f"   Players: {len(cache.core_data.get('players', {}))}")
        logger.info(f"   Teams: {len(cache.core_data.get('teams', {}))}")
    except Exception as e:
        logger.error(f"❌ Failed to load core game data on startup: {e}", exc_info=True)
        logger.warning("The API may have degraded performance until data is loaded.")

# Configure CORS - set FRONTEND_URLS env var to comma-separated allowed origins (or leave unset to allow all)
_frontend_urls = os.getenv("FRONTEND_URLS")
if _frontend_urls:
    origins = [u.strip() for u in _frontend_urls.split(",") if u.strip()]
else:
    origins = ["*"]

# Starlette/FastAPI disallow credentials with wildcard origins. Adjust dynamically.
allow_credentials = True
if origins == ["*"]:
    allow_credentials = False
    logger.warning(
        "CORS configured with allow_origins='*'. Disabling credentials. "
        "Set FRONTEND_URLS to a comma-separated list to enable credentials."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request / response models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    # kept for backwards-compatibility; agent manages its own tools
    tools: Optional[List[str]] = None

class QueryResponse(BaseModel):
    answer: str
    raw_output: Optional[Any] = None

_AGENT_CACHE: Dict[str, Any] = {}
_CHAT_HISTORY_CACHE: Dict[str, List[Any]] = {}

# Helper to create an agent using the project's main implementation
def _get_or_create_agent(session_id: str) -> Any:
    agent = _AGENT_CACHE.get(session_id)
    if agent is None:
        logger.info("Creating agent for session=%s", session_id)
        agent = create_agent()
        _AGENT_CACHE[session_id] = agent
    return agent

# Ensure a chat history list exists per session
def _get_chat_history(session_id: str) -> List[Any]:
    hist = _CHAT_HISTORY_CACHE.get(session_id)
    if hist is None:
        hist = []
        _CHAT_HISTORY_CACHE[session_id] = hist
    return hist

# Async wrapper to run agent.invoke in a worker thread (sync API)
def _extract_status_code(exc: Exception) -> Optional[int]:
    """Try to pull an HTTP-ish status code off the exception."""
    for attr in ("status", "status_code", "code"):
        value = getattr(exc, attr, None)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    match = re.search(r"\b([45]\d{2})\b", str(exc))
    if match:
        return int(match.group(1))
    return None


def _is_model_overloaded(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "model is overloaded" in msg or _extract_status_code(exc) == 503


def _coerce_to_text(payload: Any) -> str:
    """Flatten structured provider output into a plain string for clients."""
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, (bytes, bytearray)):
        return payload.decode("utf-8", errors="replace")
    if isinstance(payload, dict):
        if "text" in payload:
            return _coerce_to_text(payload.get("text"))
        if "content" in payload:
            return _coerce_to_text(payload.get("content"))
        return str(payload)
    if isinstance(payload, Iterable):
        parts: List[str] = []
        for item in payload:
            text = _coerce_to_text(item)
            if text:
                parts.append(text)
        return "\n".join(parts)
    return str(payload)


async def _invoke_agent(agent: Any, query: str, chat_history: List[Any]) -> Any:
    payload = {"input": query, "chat_history": chat_history}
    delay = 2.0
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            return await asyncio.to_thread(agent.invoke, payload)
        except Exception as exc:
            if attempt == max_attempts or not _is_model_overloaded(exc):
                raise
            logger.warning(
                "Agent invoke attempt %s/%s failed with potential overload. Retrying in %.1fs...",
                attempt,
                max_attempts,
                delay,
            )
            await asyncio.sleep(delay)
            delay *= 2

@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    """
    Accepts JSON: { "query": "...", "session_id": "optional" }
    Creates or reuses an agent per session_id and maintains per-session chat history.
    """
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="query must be a non-empty string")

    session = req.session_id or "_default"
    agent = _get_or_create_agent(session)
    chat_history = _get_chat_history(session)

    try:
        logger.info("Running agent for session=%s query=%s", session, req.query[:120])
        result = await _invoke_agent(agent, req.query, chat_history)

        # Extract response and update chat history
        response_raw = result.get("output") if isinstance(result, dict) else result
        response_text = _coerce_to_text(response_raw if response_raw is not None else result)
        chat_history.append(HumanMessage(content=req.query))
        chat_history.append(AIMessage(content=response_text))

        return QueryResponse(answer=response_text, raw_output=None)
    except Exception as e:
        logger.exception("Agent run failed")
        if _is_model_overloaded(e):
            raise HTTPException(
                status_code=503,
                detail="The language model provider is temporarily overloaded. Please try again shortly.",
            ) from e
        raise HTTPException(status_code=500, detail="Agent failed to process the request.") from e

@app.get("/api/health")
async def health():
    return {"status": "ok"}