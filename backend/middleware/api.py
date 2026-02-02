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
from backend.database.db import (
    get_all_chat_sessions, 
    create_chat_session, 
    delete_chat_session, 
    get_chat_history_db, 
    save_chat_message,
    update_chat_title
)
from backend.agent.memory import serialize_message, deserialize_message

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
    manager_id: Optional[int] = None
    # kept for backwards-compatibility; agent manages its own tools
    tools: Optional[List[str]] = None

class QueryResponse(BaseModel):
    answer: str
    raw_output: Optional[Any] = None

_AGENT_CACHE: Dict[str, Any] = {}
# _CHAT_HISTORY_CACHE removed in favor of DB persistence

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
    raw_history = get_chat_history_db(session_id)
    if not raw_history:
        return []
    return [deserialize_message(m) for m in raw_history]

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


async def _invoke_agent(agent: Any, query: str, chat_history: List[Any], manager_id: Optional[int] = None) -> Any:
    # If manager_id is provided, prepend it as context to the query
    # This way the agent knows the user's FPL ID without having to ask
    if manager_id is not None:
        enhanced_query = f"[User's FPL Team ID: {manager_id}]\n\n{query}"
    else:
        enhanced_query = query
    
    payload = {"input": enhanced_query, "chat_history": chat_history}
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
        logger.info("Running agent for session=%s query=%s manager_id=%s", session, req.query[:120], req.manager_id)
        result = await _invoke_agent(agent, req.query, chat_history, req.manager_id)

        # Extract response and update chat history
        response_raw = result.get("output") if isinstance(result, dict) else result
        response_text = _coerce_to_text(response_raw if response_raw is not None else result)
        
        # Save to DB persistence
        human_msg = HumanMessage(content=req.query)
        ai_msg = AIMessage(content=response_text)
        
        save_chat_message(session, serialize_message(human_msg))
        save_chat_message(session, serialize_message(ai_msg))

        return QueryResponse(answer=response_text, raw_output=None)
    except Exception as e:
        logger.exception("Agent run failed")
        if _is_model_overloaded(e):
            raise HTTPException(
                status_code=503,
                detail="The language model provider is temporarily overloaded. Please try again shortly.",
            ) from e
        raise HTTPException(status_code=500, detail="Agent failed to process the request.") from e

@app.get("/api/chats")
async def list_chats():
    """List all chat sessions."""
    return get_all_chat_sessions()

@app.post("/api/chats")
async def create_new_chat():
    """Create a new chat session."""
    session_id = create_chat_session()
    return {"session_id": session_id}

@app.delete("/api/chats/{session_id}")
async def delete_chat(session_id: str):
    """Delete a chat session."""
    delete_chat_session(session_id)
    # Also clear from memory cache if present
    if session_id in _AGENT_CACHE:
        del _AGENT_CACHE[session_id]
    return {"status": "deleted"}

@app.get("/api/chats/{session_id}")
async def get_chat_details(session_id: str):
    """Get chat history for a session."""
    history = _get_chat_history(session_id)
    # Convert back to serializable format for frontend
    return {"history": [serialize_message(m) for m in history]}

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/manager/{entry_id}")
async def get_manager(entry_id: int):
    """
    Get manager information by FPL entry ID.
    Returns basic manager info, current GW points, and league standings.
    """
    from backend.data import api_client
    
    try:
        # Get manager summary
        summary = await asyncio.to_thread(api_client.entry_summary, entry_id)
        
        # Get manager history for current season stats
        history = await asyncio.to_thread(api_client.entry_history, entry_id)
        
        # Extract current gameweek data
        current_gw = history.get("current", [])
        latest_gw = current_gw[-1] if current_gw else {}
        
        # Extract classic leagues (limit to top 5 by rank)
        leagues = summary.get("leagues", {}).get("classic", [])
        top_leagues = sorted(
            [{"id": l["id"], "name": l["name"], "rank": l["entry_rank"]} for l in leagues if l.get("entry_rank")],
            key=lambda x: x["rank"]
        )[:5]
        
        return {
            "id": summary.get("id"),
            "name": f"{summary.get('player_first_name', '')} {summary.get('player_last_name', '')}".strip(),
            "team_name": summary.get("name", ""),
            "overall_rank": summary.get("summary_overall_rank"),
            "overall_points": summary.get("summary_overall_points", 0),
            "gameweek_points": latest_gw.get("points", 0),
            "team_value": latest_gw.get("value", 0) / 10,  # Convert to millions
            "bank": latest_gw.get("bank", 0) / 10,  # Convert to millions
            "total_transfers": summary.get("last_deadline_total_transfers", 0),
            "leagues": top_leagues,
        }
    except Exception as e:
        logger.exception(f"Failed to get manager info for entry_id={entry_id}")
        raise HTTPException(status_code=404, detail=f"Manager with ID {entry_id} not found or API error.")


@app.get("/api/manager/{entry_id}/team")
async def get_manager_team(entry_id: int, event: int = None):
    """
    Get a manager's full team for a specific gameweek.
    If event (gameweek) is not provided, uses the current gameweek.
    Returns the team with player details including name, position, team, points, etc.
    """
    from backend.data.manager.manager_data import get_manager_squad_data
    
    try:
        result = await asyncio.to_thread(get_manager_squad_data, entry_id, event)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get team for entry_id={entry_id}, event={event}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch team data: {str(e)}")

@app.get("/api/news")
async def get_player_news():
    """
    Get the latest player news (injuries, price changes) from MongoDB.
    """
    from backend.data.core.cache import get_cached_player_news
    
    try:
        # Run in thread to avoid blocking
        alerts = await asyncio.to_thread(get_cached_player_news)
        return alerts
    except Exception as e:
        logger.exception("Failed to fetch player news")
        return []

@app.post("/api/news/refresh")
async def refresh_player_news():
    """
    Manually trigger a refresh of videoprinter data (price changes, injuries, match events).
    This only updates short-term live data, not static player/team data.
    """
    from backend.database.ingestion import update_videoprinter_data
    
    try:
        logger.info("Manual videoprinter refresh triggered")
        # Run in thread to avoid blocking
        await asyncio.to_thread(update_videoprinter_data)
        # Return fresh data
        from backend.data.core.cache import get_cached_player_news
        alerts = await asyncio.to_thread(get_cached_player_news)
        return {"success": True, "message": "Data refreshed", "data": alerts}
    except Exception as e:
        logger.exception("Failed to refresh videoprinter data")
        raise HTTPException(status_code=500, detail=f"Failed to refresh data: {str(e)}")