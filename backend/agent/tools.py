"""Tool definitions exposed to the LLM.

All tools use the unified `langchain_core.tools.tool` decorator for consistency
with LangChain 1.x + LangGraph. Each function wraps underlying data-layer
helpers and returns raw dicts/objects suitable for the agent to format.
"""

from typing import Optional, Any, Dict, List
from ..data import api_client, cache, livefpl_scrape, stats
from langchain_core.tools import tool


# -----------------------------
# PLAYER + STATS TOOLS
# -----------------------------

@tool
def get_all_players_with_stats(session: Optional[Any] = None, timeout: Optional[int] = None) -> List[Dict]:
    """Get all players with calculated statistics (PPM, points per 90, etc.)."""
    return stats.get_all_players_with_stats(session=session, timeout=timeout)


@tool
def get_player_stats(player_name: str, session: Optional[Any] = None, timeout: Optional[int] = None) -> Dict:
    """Get stats for a specific player by name."""
    return stats.get_player_stats(player_name, session=session, timeout=timeout)


@tool
def get_best_players(
    position: Optional[str] = None,
    sort_by: str = "points_per_million_per_90",
    count: int = 5,
    session: Optional[Any] = None,
    timeout: Optional[int] = None,
) -> List[Dict]:
    """Return the best players by position and sort criteria."""
    return stats.get_best_players(
        position=position,
        sort_by=sort_by,
        count=count,
        session=session,
        timeout=timeout
    )


# -----------------------------
# RULES + LOOKUP TOOLS
# -----------------------------

@tool
def get_fpl_rules() -> Dict:
    """Return the full FPL rules knowledge base + formatted string."""
    return stats.get_fpl_rules()


@tool
def get_player_by_name(player_name: str) -> Dict:
    """Fast lookup for one specific player."""
    return cache.get_player_by_name(player_name)


@tool
def get_current_gameweek() -> int:
    """Get the current gameweek number."""
    return cache.get_current_gameweek()


@tool
def get_team_by_name(team_name: str) -> Dict:
    """Get information about a specific Premier League team."""
    return cache.get_team_by_name(team_name)


# -----------------------------
# DATA LOADING TOOLS
# -----------------------------

@tool
def load_core_game_data(session: Optional[Any] = None, timeout: Optional[int] = None) -> Dict:
    """Load all core FPL data (players, teams, gameweeks, fixtures)."""
    return cache.load_core_game_data(session=session, timeout=timeout)


# -----------------------------
# LIVEFPL SCRAPER
# -----------------------------

@tool
def scrape_livefpl_data(entry_id: int, headless: bool = True, timeout: int = 180000) -> Dict:
    """Scrape FPL data from plan.livefpl.net for a given entry ID."""
    return livefpl_scrape.scrape_livefpl_data(entry_id, headless=headless, timeout=timeout)


# -----------------------------
# FPL API CLIENT
# -----------------------------

@tool
def bootstrap_static(session: Optional[Any] = None, timeout: Optional[int] = None) -> Dict:
    """Get bootstrap-static data (events, elements, teams, etc.)."""
    return api_client.bootstrap_static(session=session, timeout=timeout)


@tool
def event_live(event_id: int, session: Optional[Any] = None, timeout: Optional[int] = None) -> Dict:
    """Get live event data for a specific gameweek."""
    return api_client.event_live(event_id, session=session, timeout=timeout)


# -----------------------------
# MANAGER-LEVEL DATA
# -----------------------------

@tool
def get_manager_info(entry_id: int, session: Optional[Any] = None, timeout: Optional[int] = None) -> Dict:
    """Get a manager's profile (team name, OR, team value)."""
    return api_client.entry_summary(entry_id, session=session, timeout=timeout)


@tool
def get_live_gameweek_data(entry_id: int, session: Optional[Any] = None, timeout: Optional[int] = None) -> Dict:
    """Get a manager's live GW performance."""
    return livefpl_scrape.scrape_livefpl_data(entry_id)


# -----------------------------
# EXPORT TOOL LIST
# -----------------------------

all_tools = [
    get_all_players_with_stats,
    get_player_stats,
    get_best_players,
    get_fpl_rules,
    get_player_by_name,
    get_current_gameweek,
    get_team_by_name,
    load_core_game_data,
    scrape_livefpl_data,
    bootstrap_static,
    event_live,
    get_manager_info,
    get_live_gameweek_data,
]
