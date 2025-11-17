"""FPL player statistics - calculated metrics and analysis"""

from langchain_core.tools import tool
from typing import Any, Dict, Optional, List
import requests
from .api_client import bootstrap_static, DEFAULT_TIMEOUT
from .fpl_rules import FPL_RULES_KNOWLEDGE, FPL_SEARCHABLE_RULES

@tool
def get_all_players_with_stats(
    session: Optional[requests.Session] = None, timeout: float = DEFAULT_TIMEOUT
) -> List[Dict[str, Any]]:
    """Get all players with calculated statistics (PPM, points per 90, etc.).

    Excludes players who transferred out of the Premier League (e.g., Harry Kane).
    Injured players are included as they are still active FPL assets.

    Returns:
        List of dicts with player info and calculated stats.
    """
    bootstrap = bootstrap_static(session=session, timeout=timeout)
    players_with_stats = []

    for element in bootstrap.get("elements", []):
        # Skip players who transferred out (status = 'u' for unavailable/transferred)
        # Keep injured players (status = 'i', 'd', 's') as they're still active
        status = element.get("status", "a")
        if status == "u":  # 'u' = transferred out of Premier League
            continue

        total_score = element.get("total_points", 0)
        minutes_played = element.get("minutes", 0)
        cost = element.get("now_cost", 0) / 10.0
        position = element.get("element_type", 0)
        points_per_game = float(element.get("points_per_game", 0))
        bonus = element.get("bonus", 0)
        assists = element.get("assists", 0)

        # Calculate derived stats
        points_per_game_per_million = (
            round(points_per_game / cost, 2) if cost > 0 else 0
        )
        appearances = minutes_played / 90.0
        points_per_90 = round(total_score / appearances, 2) if appearances > 0 else 0
        points_per_million = round(total_score / cost, 2) if cost > 0 else 0
        points_per_million_per_90 = (
            round(points_per_90 / cost, 2) if cost > 0 else 0
        )
        bonus_per_90 = round(bonus / appearances, 2) if appearances > 0 else 0

        player_stat = {
            "id": element.get("id"),
            "name": element.get("web_name"),
            "full_name": f"{element.get('first_name', '')} {element.get('second_name', '')}".strip(),
            "position": position,
            "team": element.get("team"),
            "total_points": total_score,
            "minutes_played": minutes_played,
            "cost": cost,
            "points_per_game": points_per_game,
            "points_per_game_per_million": points_per_game_per_million,
            "bonus_per_90": bonus_per_90,
            "points_per_90": points_per_90,
            "points_per_million": points_per_million,
            "points_per_million_per_90": points_per_million_per_90,
            "assists": assists,
            "selected_by_percent": float(element.get("selected_by_percent", 0)),
            "form": float(element.get("form", 0)),
        }

        players_with_stats.append(player_stat)

    return players_with_stats

@tool
def get_player_stats(player_name: str, session: Optional[requests.Session] = None, timeout: float = DEFAULT_TIMEOUT) -> Optional[Dict[str, Any]]:
    """Get stats for a specific player by name."""
    bootstrap = bootstrap_static(session=session, timeout=timeout)
    for element in bootstrap.get("elements", []):
        if element.get("web_name", "").lower() == player_name.lower():
            return element
    return None

@tool
def get_best_players(position: str = None, sort_by: str = "points_per_million_per_90", count: int = 5, session: Optional[requests.Session] = None, timeout: float = DEFAULT_TIMEOUT) -> list:
    """Return the best players by position and sort criteria."""
    players = get_all_players_with_stats(session=session, timeout=timeout)
    position_map = {"gk": 1, "def": 2, "mid": 3, "fwd": 4, "goalkeeper": 1, "defender": 2, "midfielder": 3, "forward": 4}
    if position:
        pos_id = position_map.get(position.lower())
        if pos_id:
            players = [p for p in players if p.get("position") == pos_id]
    if sort_by:
        players = sorted(players, key=lambda x: x.get(sort_by, 0), reverse=True)
    return players[:count]



@tool
def get_fpl_rules() -> dict:
    """Return the full FPL rules knowledge base and a formatted string for conversational use."""
    return {
        "knowledge_base": FPL_RULES_KNOWLEDGE,
        "searchable_rules": FPL_SEARCHABLE_RULES
    }
