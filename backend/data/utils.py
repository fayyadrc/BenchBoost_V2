"""
Shared utility functions for FPL data processing.
Consolidates common patterns to avoid duplication across modules.
"""

from typing import Dict, Any, Optional, List
from .constants import POSITION_ID_TO_NAME


def get_player_full_name(player: Dict[str, Any]) -> str:
    """
    Construct full name from player dict.
    
    Args:
        player: Player dict with first_name and second_name fields
        
    Returns:
        Full name string (e.g., "Mohamed Salah")
    """
    first = player.get("first_name", "")
    second = player.get("second_name", "")
    return f"{first} {second}".strip()


def get_position_name(element_type: int) -> str:
    """
    Convert position ID to position name.
    
    Args:
        element_type: Position ID (1-4)
        
    Returns:
        Position name (GKP, DEF, MID, FWD)
    """
    return POSITION_ID_TO_NAME.get(element_type, "UNK")


def calculate_player_stats(player: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate derived statistics for a player.
    
    Args:
        player: Raw player dict from FPL API
        
    Returns:
        Dict with calculated stats (PPM, points_per_90, etc.)
    """
    total_points = player.get("total_points", 0)
    minutes_played = player.get("minutes", 0)
    cost = player.get("now_cost", 0) / 10  # Convert to millions
    points_per_game = float(player.get("points_per_game", 0) or 0)
    
    # Calculate appearances (90 minute equivalents)
    appearances = minutes_played / 90.0 if minutes_played > 0 else 0
    
    # Points per 90 minutes
    points_per_90 = round(total_points / appearances, 2) if appearances > 0 else 0
    
    # Points per million (value)
    points_per_million = round(total_points / cost, 2) if cost > 0 else 0
    
    # Points per game per million
    points_per_game_per_million = round(points_per_game / cost, 2) if cost > 0 else 0
    
    return {
        "points_per_90": points_per_90,
        "points_per_million": points_per_million,
        "points_per_game_per_million": points_per_game_per_million,
        "appearances_90": round(appearances, 1),
    }


def enrich_player_data(
    player: Dict[str, Any],
    team: Optional[Dict[str, Any]] = None,
    live_stats: Optional[Dict[str, Any]] = None,
    include_calculated_stats: bool = True
) -> Dict[str, Any]:
    """
    Enrich raw player data with team info, position names, and calculated stats.
    
    This is the single source of truth for player data enrichment.
    
    Args:
        player: Raw player dict from FPL API or cache
        team: Optional team dict for team name/short_name
        live_stats: Optional live gameweek stats dict
        include_calculated_stats: Whether to include PPM, points_per_90, etc.
        
    Returns:
        Enriched player dict
    """
    enriched = {
        "id": player.get("id"),
        "web_name": player.get("web_name", "Unknown"),
        "full_name": get_player_full_name(player),
        "position": get_position_name(player.get("element_type", 0)),
        "element_type": player.get("element_type"),
        "price": player.get("now_cost", 0) / 10,
        "form": player.get("form", "0"),
        "points_per_game": player.get("points_per_game", "0"),
        "total_points": player.get("total_points", 0),
        "minutes": player.get("minutes", 0),
        "selected_by_percent": player.get("selected_by_percent", "0"),
        "news": player.get("news", ""),
        "chance_of_playing": player.get("chance_of_playing_next_round"),
        "photo": player.get("photo", ""),
    }
    
    # Add team info if provided
    if team:
        enriched["team_name"] = team.get("name", "Unknown")
        enriched["team_short"] = team.get("short_name", "UNK")
        enriched["team_id"] = team.get("id")
    else:
        enriched["team_name"] = "Unknown"
        enriched["team_short"] = "UNK"
        enriched["team_id"] = player.get("team")
    
    # Add live stats if provided
    if live_stats:
        enriched["gw_points"] = live_stats.get("total_points", 0)
        enriched["gw_minutes"] = live_stats.get("minutes", 0)
    
    # Add calculated stats if requested
    if include_calculated_stats:
        calculated = calculate_player_stats(player)
        enriched.update(calculated)
    
    return enriched


def parse_player_and_team(raw_text: str) -> Dict[str, Optional[str]]:
    """
    Parse player name and team from text like "Salah (LIV)".
    
    Used by scrapers to extract structured data from text.
    
    Args:
        raw_text: Text like "Salah (LIV)" or just "Salah"
        
    Returns:
        Dict with 'player' and 'team' keys
    """
    if "(" not in raw_text or not raw_text.endswith(")"):
        return {"player": raw_text.strip(), "team": None}
    
    player_part, team_part = raw_text.rsplit("(", 1)
    return {
        "player": player_part.strip(),
        "team": team_part.rstrip(")").strip() or None,
    }


def parse_price(price_text: str) -> float:
    """
    Parse price text like "£10.5m" or "10.5" to float.
    
    Args:
        price_text: Price string in various formats
        
    Returns:
        Price as float in millions
    """
    if not price_text:
        return 0.0
    
    # Remove currency symbols and 'm' suffix
    cleaned = price_text.replace("£", "").replace("m", "").replace(",", "").strip()
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def format_price(price: float) -> str:
    """
    Format price as £X.Xm string.
    
    Args:
        price: Price in millions
        
    Returns:
        Formatted string like "£10.5m"
    """
    return f"£{price:.1f}m"
