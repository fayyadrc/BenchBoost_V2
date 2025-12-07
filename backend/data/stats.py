"""FPL player statistics - calculated metrics and analysis"""

from typing import Any, Dict, Optional, List
from datetime import datetime
import requests
from .api_client import bootstrap_static, DEFAULT_TIMEOUT
from .fpl_rules import FPL_RULES_KNOWLEDGE, FPL_SEARCHABLE_RULES
from .utils import (
    get_player_full_name,
    get_position_name,
    calculate_player_stats,
    calculate_expected_performance,
    classify_ownership,
    classify_form,
    classify_price,
    classify_transfer_trend,
    enrich_player_data,
)
from .constants import POSITION_NAME_TO_ID, VALID_PLAYER_METRICS


def get_all_players_with_stats(
    session: Optional[requests.Session] = None, 
    timeout: float = DEFAULT_TIMEOUT,
    include_expected: bool = True,
    include_classifications: bool = True,
) -> List[Dict[str, Any]]:
    """Get all players with calculated statistics (PPM, points per 90, etc.).

    Excludes players who transferred out of the Premier League (e.g., Harry Kane).
    Injured players are included as they are still active FPL assets.

    Args:
        session: Optional requests session
        timeout: Request timeout
        include_expected: Include xG/xA analysis
        include_classifications: Include ownership/form/price tiers
        
    Returns:
        List of dicts with player info and calculated stats.
    """
    bootstrap = bootstrap_static(session=session, timeout=timeout)
    teams = {t["id"]: t for t in bootstrap.get("teams", [])}
    players_with_stats = []

    for element in bootstrap.get("elements", []):
        # Skip players who transferred out (status = 'u' for unavailable/transferred)
        # Keep injured players (status = 'i', 'd', 's') as they're still active
        status = element.get("status", "a")
        if status == "u":  # 'u' = transferred out of Premier League
            continue

        # Get team info
        team = teams.get(element.get("team"))
        
        # Use the standardized enrichment function
        enriched = enrich_player_data(
            element,
            team=team,
            include_calculated_stats=True,
            include_expected_stats=include_expected,
            include_classifications=include_classifications,
        )
        
        # Add transfer info
        enriched["transfers_in_event"] = element.get("transfers_in_event", 0)
        enriched["transfers_out_event"] = element.get("transfers_out_event", 0)
        enriched["transfers_in"] = element.get("transfers_in", 0)
        enriched["transfers_out"] = element.get("transfers_out", 0)
        
        # Add metadata
        enriched["_meta"] = {
            "fetched_at": datetime.now().isoformat(),
            "source": "fpl_api",
        }

        players_with_stats.append(enriched)

    return players_with_stats

def get_player_stats(
    player_name: str, 
    session: Optional[requests.Session] = None, 
    timeout: float = DEFAULT_TIMEOUT,
    include_expected: bool = True,
    include_classifications: bool = True,
) -> Optional[Dict[str, Any]]:
    """Get stats for a specific player by name.

    Matching logic:
    1. Exact match on web_name (e.g. "Haaland").
    2. Exact match on full name ("Erling Haaland").
    3. Case-insensitive substring match against web_name or full name.
    4. Token match: all tokens contained within the player's full name.

    Args:
        player_name: Player name to search for
        session: Optional requests session
        timeout: Request timeout
        include_expected: Include xG/xA analysis
        include_classifications: Include ownership/form/price tiers
        
    Returns:
        Enriched player dict or None if not found
    """
    target = player_name.strip().lower()
    if not target:
        return None

    bootstrap = bootstrap_static(session=session, timeout=timeout)
    candidates = bootstrap.get("elements", [])
    teams = {t["id"]: t for t in bootstrap.get("teams", [])}

    def enrich(element: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich player with full stats using standardized utilities."""
        team = teams.get(element.get("team"))
        enriched = enrich_player_data(
            element,
            team=team,
            include_calculated_stats=True,
            include_expected_stats=include_expected,
            include_classifications=include_classifications,
        )
        
        # Add transfer info
        enriched["transfers_in_event"] = element.get("transfers_in_event", 0)
        enriched["transfers_out_event"] = element.get("transfers_out_event", 0)
        enriched["transfers_in"] = element.get("transfers_in", 0)
        enriched["transfers_out"] = element.get("transfers_out", 0)
        
        # Add metadata
        enriched["_meta"] = {
            "fetched_at": datetime.now().isoformat(),
            "source": "fpl_api",
            "search_query": player_name,
        }
        
        return enriched

    # Build searchable strings - exact match first
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


def get_best_players(
    position: str = None, 
    sort_by: str = "points_per_million", 
    count: int = 5, 
    min_minutes: int = 90,
    session: Optional[requests.Session] = None, 
    timeout: float = DEFAULT_TIMEOUT
) -> List[Dict[str, Any]]:
    """Return the best players by position and sort criteria.
    
    Args:
        position: Position filter (GK, DEF, MID, FWD) or None for all
        sort_by: Metric to sort by (see VALID_PLAYER_METRICS)
        count: Number of players to return
        min_minutes: Minimum minutes played filter (default 90)
        session: Optional requests session
        timeout: Request timeout
        
    Returns:
        List of top players sorted by the specified metric
    """
    players = get_all_players_with_stats(session=session, timeout=timeout)
    
    # Filter by minimum minutes
    players = [p for p in players if p.get("minutes", 0) >= min_minutes]
    
    # Filter by position
    if position:
        pos_normalized = position.upper()
        pos_id = POSITION_NAME_TO_ID.get(pos_normalized)
        if pos_id:
            players = [p for p in players if p.get("element_type") == pos_id]
    
    # Handle nested stats for sorting
    def get_sort_value(player: Dict, key: str) -> float:
        # Check top level first
        if key in player:
            val = player.get(key, 0)
        # Then check derived_stats
        elif player.get("derived_stats") and key in player.get("derived_stats", {}):
            val = player["derived_stats"].get(key, 0)
        # Then check expected_stats
        elif player.get("expected_stats") and key in player.get("expected_stats", {}):
            val = player["expected_stats"].get(key, 0)
        else:
            val = 0
        
        # Ensure we return a number
        try:
            return float(val) if val else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    # Sort by metric
    if sort_by:
        players = sorted(players, key=lambda x: get_sort_value(x, sort_by), reverse=True)
    
    return players[:count]


def get_transfer_trends(
    count: int = 10,
    direction: str = "in",
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT
) -> List[Dict[str, Any]]:
    """Get most transferred in/out players.
    
    Args:
        count: Number of players to return
        direction: "in" for most transferred in, "out" for most transferred out
        session: Optional requests session
        timeout: Request timeout
        
    Returns:
        List of players with transfer data, sorted by transfer volume
    """
    players = get_all_players_with_stats(session=session, timeout=timeout)
    
    sort_key = "transfers_in_event" if direction == "in" else "transfers_out_event"
    players = sorted(players, key=lambda x: x.get(sort_key, 0), reverse=True)
    
    return players[:count]


def get_differentials(
    max_ownership: float = 10.0,
    min_form: float = 4.0,
    min_minutes: int = 180,
    position: Optional[str] = None,
    count: int = 10,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT
) -> List[Dict[str, Any]]:
    """Find differential players with low ownership but good form/stats.
    
    Args:
        max_ownership: Maximum ownership percentage
        min_form: Minimum form rating
        min_minutes: Minimum minutes played
        position: Optional position filter
        count: Number of players to return
        session: Optional requests session
        timeout: Request timeout
        
    Returns:
        List of differential players sorted by form
    """
    players = get_all_players_with_stats(session=session, timeout=timeout)
    
    # Apply filters
    differentials = [
        p for p in players
        if p.get("selected_by_percent", 100) <= max_ownership
        and p.get("form", 0) >= min_form
        and p.get("minutes", 0) >= min_minutes
    ]
    
    # Position filter
    if position:
        pos_id = POSITION_NAME_TO_ID.get(position.upper())
        if pos_id:
            differentials = [p for p in differentials if p.get("element_type") == pos_id]
    
    # Sort by form
    differentials = sorted(differentials, key=lambda x: x.get("form", 0), reverse=True)
    
    return differentials[:count]


def get_underperformers(
    min_xg_difference: float = -1.0,
    min_minutes: int = 270,
    count: int = 10,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT
) -> List[Dict[str, Any]]:
    """Find players underperforming their xG (potential value picks).
    
    Players scoring fewer goals than their xG suggests are likely to improve.
    
    Args:
        min_xg_difference: Minimum goals - xG difference (negative = underperforming)
        min_minutes: Minimum minutes played
        count: Number of players to return
        session: Optional requests session
        timeout: Request timeout
        
    Returns:
        List of underperforming players (could be due for a goals burst)
    """
    players = get_all_players_with_stats(
        session=session, 
        timeout=timeout,
        include_expected=True
    )
    
    # Filter for players with expected stats and enough minutes
    underperformers = []
    for p in players:
        if p.get("minutes", 0) < min_minutes:
            continue
        
        expected = p.get("expected_stats", {})
        xg_diff = expected.get("goals_vs_xg", 0)
        
        # Negative xG difference = scoring less than expected
        if xg_diff <= min_xg_difference:
            p["xg_difference"] = xg_diff
            underperformers.append(p)
    
    # Sort by most underperforming (most negative first)
    underperformers = sorted(underperformers, key=lambda x: x.get("xg_difference", 0))
    
    return underperformers[:count]


def get_overperformers(
    min_xg_difference: float = 1.0,
    min_minutes: int = 270,
    count: int = 10,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT
) -> List[Dict[str, Any]]:
    """Find players overperforming their xG (potential regression candidates).
    
    Players scoring more goals than their xG suggests may regress.
    
    Args:
        min_xg_difference: Minimum goals - xG difference (positive = overperforming)
        min_minutes: Minimum minutes played
        count: Number of players to return
        session: Optional requests session
        timeout: Request timeout
        
    Returns:
        List of overperforming players (might regress to mean)
    """
    players = get_all_players_with_stats(
        session=session, 
        timeout=timeout,
        include_expected=True
    )
    
    overperformers = []
    for p in players:
        if p.get("minutes", 0) < min_minutes:
            continue
        
        expected = p.get("expected_stats", {})
        xg_diff = expected.get("goals_vs_xg", 0)
        
        if xg_diff >= min_xg_difference:
            p["xg_difference"] = xg_diff
            overperformers.append(p)
    
    # Sort by most overperforming
    overperformers = sorted(overperformers, key=lambda x: x.get("xg_difference", 0), reverse=True)
    
    return overperformers[:count]


def get_fpl_rules() -> dict:
    """Return the full FPL rules knowledge base and a formatted string for conversational use."""
    return {
        "knowledge_base": FPL_RULES_KNOWLEDGE,
        "searchable_rules": FPL_SEARCHABLE_RULES,
        "_meta": {
            "fetched_at": datetime.now().isoformat(),
            "source": "static_rules",
        }
    }
