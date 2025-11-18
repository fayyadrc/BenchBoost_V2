"""FPL player statistics - calculated metrics and analysis"""

from typing import Any, Dict, Optional, List
import requests
from .api_client import bootstrap_static, DEFAULT_TIMEOUT
from .fpl_rules import FPL_RULES_KNOWLEDGE, FPL_SEARCHABLE_RULES

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

def get_player_stats(player_name: str, session: Optional[requests.Session] = None, timeout: float = DEFAULT_TIMEOUT) -> Optional[Dict[str, Any]]:
    """Get stats for a specific player by name.

    Matching logic:
    1. Exact match on web_name (e.g. "Haaland").
    2. Exact match on full name ("Erling Haaland").
    3. Case-insensitive substring match against web_name or full name.
    4. Token match: all tokens contained within the player's full name.

    Returns the raw element dict augmented with a few derived stats for consistency
    with get_all_players_with_stats.
    """
    target = player_name.strip().lower()
    if not target:
        return None

    bootstrap = bootstrap_static(session=session, timeout=timeout)
    candidates = bootstrap.get("elements", [])

    def enrich(element: Dict[str, Any]) -> Dict[str, Any]:
        # Mirror derived stats from get_all_players_with_stats for a single player
        total_score = element.get("total_points", 0)
        minutes_played = element.get("minutes", 0)
        cost = element.get("now_cost", 0) / 10.0
        points_per_game = float(element.get("points_per_game", 0))
        bonus = element.get("bonus", 0)
        assists = element.get("assists", 0)
        appearances = minutes_played / 90.0 if minutes_played else 0
        points_per_90 = round(total_score / appearances, 2) if appearances > 0 else 0
        points_per_million = round(total_score / cost, 2) if cost > 0 else 0
        points_per_game_per_million = round(points_per_game / cost, 2) if cost > 0 else 0
        points_per_million_per_90 = round(points_per_90 / cost, 2) if cost > 0 else 0
        bonus_per_90 = round(bonus / appearances, 2) if appearances > 0 else 0
        element["derived_stats"] = {
            "points_per_90": points_per_90,
            "points_per_million": points_per_million,
            "points_per_game_per_million": points_per_game_per_million,
            "points_per_million_per_90": points_per_million_per_90,
            "bonus_per_90": bonus_per_90,
            "assists": assists,
        }
        return element

    # Build searchable strings
    for element in candidates:
        web = element.get("web_name", "").lower()
        full = f"{element.get('first_name', '')} {element.get('second_name', '')}".strip().lower()
        if target == web or target == full:
            return enrich(element)

    # Substring match
    substring_hits = []
    for element in candidates:
        web = element.get("web_name", "").lower()
        full = f"{element.get('first_name', '')} {element.get('second_name', '')}".strip().lower()
        if target in web or (full and target in full):
            substring_hits.append(element)
    if substring_hits:
        return enrich(substring_hits[0])  # Return first match deterministically

    # Token match (all tokens present in full name words)
    tokens = [t for t in target.split() if t]
    if tokens:
        for element in candidates:
            full_tokens = f"{element.get('first_name', '')} {element.get('second_name', '')}".lower().split()
            if all(tok in full_tokens for tok in tokens):
                return enrich(element)

    return None

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

def get_fpl_rules() -> dict:
    """Return the full FPL rules knowledge base and a formatted string for conversational use."""
    return {
        "knowledge_base": FPL_RULES_KNOWLEDGE,
        "searchable_rules": FPL_SEARCHABLE_RULES
    }
