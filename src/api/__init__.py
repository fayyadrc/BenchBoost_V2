"""FPL API client module"""

from .client import (
    bootstrap_static,
    event_live,
    my_team,
    entry_details,
    entry_summary,
    entry_history,
    transfers_history,
    gameweek_picks,
    fixtures,
    element_summary,
    league_standings,
    fetch_public_data,
)

from .cache import (
    core_data,
    latest_data,
    load_core_game_data,
    get_player_by_id,
    get_player_by_name,
    get_team_by_id,
    get_team_by_name,
    get_gameweek_by_id,
    get_current_gameweek,
    get_fixture_by_id,
)

from .stats import get_all_players_with_stats

__all__ = [
    # API endpoints
    "bootstrap_static",
    "event_live",
    "my_team",
    "entry_details",
    "entry_summary",
    "entry_history",
    "transfers_history",
    "gameweek_picks",
    "fixtures",
    "element_summary",
    "league_standings",
    "fetch_public_data",
    # Cache functions
    "core_data",
    "latest_data",
    "load_core_game_data",
    "get_player_by_id",
    "get_player_by_name",
    "get_team_by_id",
    "get_team_by_name",
    "get_gameweek_by_id",
    "get_current_gameweek",
    "get_fixture_by_id",
    # Stats
    "get_all_players_with_stats",
]
