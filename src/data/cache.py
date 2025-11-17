"""FPL data cache - stores and provides quick access to core game data"""
 
from typing import Any, Dict, Optional
from langchain.tools import tool
import requests
from .client import bootstrap_static, fixtures, DEFAULT_TIMEOUT
 
# Module-level cache: populated when `fetch_public_data` is called with persist=True.
latest_data: Dict[str, Any] = {}
 
# Core game data dictionaries - organized for easy access
core_data: Dict[str, Any] = {
    "players": {},  # player_id -> player details
    "teams": {},  # team_id -> team details
    "gameweek": {},  # gameweek_id -> gameweek details
    "fixtures": {},  # fixture_id -> fixture details
    "players_by_name": {},  # player_name -> player details (for quick lookup)
    "teams_by_name": {},  # team_name -> team details
}
 
def load_core_game_data(
    session: Optional[requests.Session] = None, timeout: float = DEFAULT_TIMEOUT
) -> Dict[str, Any]:
    """
    Load all core FPL game data into organized dictionaries.
 
    This fetches and organizes:
    - All players (with stats, filtering out transferred players)
    - All teams
    - All gameweeks
    - All fixtures
 
    Data is stored in the module-level `core_data` dict for easy access.
 
    Returns:
        Dict with the organized core data.
    """
    global core_data
 
    # Fetch bootstrap-static (main data source)
    bs = bootstrap_static(session=session, timeout=timeout)
 
    # Organize players by ID and name
    core_data["players"] = {}
    core_data["players_by_name"] = {}
 
    for player in bs.get("elements", []):
        # Skip players who transferred out of Premier League
        if player.get("status") == "u":
            continue
 
        player_id = player.get("id")
        player_name = player.get("web_name", "")
 
        core_data["players"][player_id] = player
        if player_name:
            core_data["players_by_name"][player_name.lower()] = player
 
    # Organize teams by ID and name
    core_data["teams"] = {}
    core_data["teams_by_name"] = {}
 
    for team in bs.get("teams", []):
        team_id = team.get("id")
        team_name = team.get("name", "")
        team_short_name = team.get("short_name", "")
 
        core_data["teams"][team_id] = team
        if team_name:
            core_data["teams_by_name"][team_name.lower()] = team
        if team_short_name:
            core_data["teams_by_name"][team_short_name.lower()] = team
 
    # Organize gameweeks by ID
    core_data["gameweeks"] = {}
 
    for event in bs.get("events", []):
        event_id = event.get("id")
        core_data["gameweeks"][event_id] = event
 
    # Fetch and organize all fixtures
    all_fixtures = fixtures(session=session, timeout=timeout)
    core_data["fixtures"] = {}
 
    for fixture in all_fixtures:
        fixture_id = fixture.get("id")
        core_data["fixtures"][fixture_id] = fixture
 
    # Store full bootstrap data for reference
    core_data["bootstrap_static"] = bs
    core_data["game_settings"] = bs.get("game_settings", {})
 
    return core_data
 
def get_player_by_id(player_id: int) -> Optional[Dict[str, Any]]:
    """Get player details by ID from core_data cache."""
    return core_data.get("players", {}).get(player_id)
 
@tool
def get_player_by_name(player_name: str) -> Optional[Dict[str, Any]]:
    """Get player details by name (case-insensitive) from core_data cache."""
    return core_data.get("players_by_name", {}).get(player_name.lower())
 
def get_team_by_id(team_id: int) -> Optional[Dict[str, Any]]:
    """Get team details by ID from core_data cache."""
    return core_data.get("teams", {}).get(team_id)
 
@tool
def get_team_by_name(team_name: str) -> Optional[Dict[str, Any]]:
    """Get team details by name (case-insensitive) from core_data cache."""
    return core_data.get("teams_by_name", {}).get(team_name.lower())
 
def get_gameweek_by_id(gameweek_id: int) -> Optional[Dict[str, Any]]:
    """Get gameweek details by ID from core_data cache."""
    return core_data.get("gameweeks", {}).get(gameweek_id)
 
@tool
def get_current_gameweek() -> Optional[Dict[str, Any]]:
    """Get the current active gameweek from core_data cache."""
    for gw in core_data.get("gameweeks", {}).values():
        if gw.get("is_current"):
            return gw
    return None
 
def get_fixture_by_id(fixture_id: int) -> Optional[Dict[str, Any]]:
    """Get fixture details by ID from core_data cache."""
    return core_data.get("fixtures", {}).get(fixture_id)