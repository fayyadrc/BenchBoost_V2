import os
import asyncio
import logging
from typing import Optional, List, Any, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Use the main agent implementation
from backend.agent.agent import create_agent
from langchain_core.messages import AIMessage, HumanMessage

# /Users/fayyadrc/Documents/Programming/FPLChatbot_V2/fplAI/backend/middleware/api.py


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FPLChatbot Middleware")

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
async def _invoke_agent(agent: Any, query: str, chat_history: List[Any]) -> Any:
    payload = {"input": query, "chat_history": chat_history}
    return await asyncio.to_thread(agent.invoke, payload)

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
        response: str = result.get("output", str(result))
        chat_history.append(HumanMessage(content=req.query))
        chat_history.append(AIMessage(content=response))

        return QueryResponse(answer=response, raw_output=None)
    except Exception as e:
        logger.exception("Agent run failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "ok"}