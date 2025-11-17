"""
tools.py
This file defines all the functions the LLM can use. It imports functions from the data module and marks them with @tool.
"""

from typing import Any
from data import api_client, cache, livefpl_scrape, stats

# If you are using LangChain or similar, you might use @tool from langchain.tools
try:
    from langchain.tools import tool
except ImportError:
    # Define a dummy decorator if not available
    def tool(func):
        return func

# Example: Expose functions from data modules
@tool
def get_all_players_with_stats(session=None, timeout=None):
    """Get all players with calculated statistics (PPM, points per 90, etc.)."""
    return stats.get_all_players_with_stats(session=session, timeout=timeout)

@tool
def get_player_stats(player_name, session=None, timeout=None):
    """Get stats for a specific player by name."""
    return stats.get_player_stats(player_name, session=session, timeout=timeout)

@tool
def get_best_players(position=None, sort_by="points_per_million_per_90", count=5, session=None, timeout=None):
    """Return the best players by position and sort criteria."""
    return stats.get_best_players(position=position, sort_by=sort_by, count=count, session=session, timeout=timeout)

@tool
def get_fpl_rules():
    """Return the full FPL rules knowledge base and a formatted string for conversational use."""
    return stats.get_fpl_rules()

@tool
def get_player_by_name(player_name):
    """Get stats for one specific player (fast lookup)."""
    return cache.get_player_by_name(player_name)

@tool
def get_current_gameweek():
    """Get the current gameweek number."""
    return cache.get_current_gameweek()

@tool
def get_team_by_name(team_name):
    """Get information about a specific Premier League team."""
    return cache.get_team_by_name(team_name)

@tool
def load_core_game_data(session=None, timeout=None):
    """Load all core FPL game data into organized dictionaries (players, teams, gameweeks, fixtures)."""
    return cache.load_core_game_data(session=session, timeout=timeout)

@tool
def scrape_livefpl_data(entry_id, headless=True, timeout=180000):
    """Scrape FPL data from plan.livefpl.net for a given entry ID."""
    return livefpl_scrape.scrape_livefpl_data(entry_id, headless=headless, timeout=timeout)

@tool
def bootstrap_static(session=None, timeout=None):
    """Get bootstrap-static data (events, elements, teams, settings, etc.) from FPL API."""
    return api_client.bootstrap_static(session=session, timeout=timeout)

@tool
def event_live(event_id, session=None, timeout=None):
    """Get live event data for a specific gameweek (event_id) from FPL API."""
    return api_client.event_live(event_id, session=session, timeout=timeout)

# List of all tools for agent registration
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
]


# Live Manager Info tools
@tool
def get_manager_info(entry_id, session=None, timeout=None):
    """Get a manager's general profile (team name, overall rank, value)."""
    return api_client.entry_summary(entry_id, session=session, timeout=timeout)

@tool
def get_live_gameweek_data(entry_id, session=None, timeout=None):
    """Get a manager's live gameweek performance (rank, threats, differentials)."""
    return livefpl_scrape.scrape_livefpl_data(entry_id)
"""
tools.py
This file defines all the functions the LLM can use. It imports functions from the data module and marks them with @tool.
"""

from typing import Any
from data import api_client, cache, livefpl_scrape, stats

# If you are using LangChain or similar, you might use @tool from langchain.tools
try:
    from langchain.tools import tool
except ImportError:
    # Define a dummy decorator if not available
    def tool(func):
        return func

# Example: Expose functions from data modules
@tool
def get_all_players_with_stats(session=None, timeout=None):
    """Get all players with calculated statistics (PPM, points per 90, etc.)."""
    return stats.get_all_players_with_stats(session=session, timeout=timeout)

@tool
def get_player_stats(player_name, session=None, timeout=None):
    """Get stats for a specific player by name."""
    return stats.get_player_stats(player_name, session=session, timeout=timeout)

@tool
def get_best_players(position=None, sort_by="points_per_million_per_90", count=5, session=None, timeout=None):
    """Return the best players by position and sort criteria."""
    return stats.get_best_players(position=position, sort_by=sort_by, count=count, session=session, timeout=timeout)

@tool
def get_fpl_rules():
    """Return the full FPL rules knowledge base and a formatted string for conversational use."""
    return stats.get_fpl_rules()

@tool
def get_player_by_name(player_name):
    """Get stats for one specific player (fast lookup)."""
    return cache.get_player_by_name(player_name)

@tool
def get_current_gameweek():
    """Get the current gameweek number."""
    return cache.get_current_gameweek()

@tool
def get_team_by_name(team_name):
    """Get information about a specific Premier League team."""
    return cache.get_team_by_name(team_name)

@tool
def load_core_game_data(session=None, timeout=None):
    """Load all core FPL game data into organized dictionaries (players, teams, gameweeks, fixtures)."""
    return cache.load_core_game_data(session=session, timeout=timeout)

@tool
def scrape_livefpl_data(entry_id, headless=True, timeout=180000):
    """Scrape FPL data from plan.livefpl.net for a given entry ID."""
    return livefpl_scrape.scrape_livefpl_data(entry_id, headless=headless, timeout=timeout)

@tool
def bootstrap_static(session=None, timeout=None):
    """Get bootstrap-static data (events, elements, teams, settings, etc.) from FPL API."""
    return api_client.bootstrap_static(session=session, timeout=timeout)

@tool
def event_live(event_id, session=None, timeout=None):
    """Get live event data for a specific gameweek (event_id) from FPL API."""
    return api_client.event_live(event_id, session=session, timeout=timeout)

# List of all tools for agent registration
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
