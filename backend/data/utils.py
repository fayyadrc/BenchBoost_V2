"""
Shared utility functions for FPL data processing.
Consolidates common patterns to avoid duplication across modules.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from .constants import (
    POSITION_ID_TO_NAME, 
    POSITION_ID_TO_FULL_NAME,
    OWNERSHIP_TIERS,
    FORM_THRESHOLDS,
    VALUE_THRESHOLDS,
    TRANSFER_THRESHOLDS,
    FIXTURE_DIFFICULTY,
    METRIC_DISPLAY_NAMES,
    AVAILABILITY_STATUS,
)


# =============================================================================
# NAME & POSITION UTILITIES
# =============================================================================

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


def get_position_full_name(element_type: int) -> str:
    """
    Convert position ID to full position name.
    
    Args:
        element_type: Position ID (1-4)
        
    Returns:
        Full position name (Goalkeeper, Defender, etc.)
    """
    return POSITION_ID_TO_FULL_NAME.get(element_type, "Unknown")


# =============================================================================
# STATISTICS CALCULATIONS
# =============================================================================

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
    goals = player.get("goals_scored", 0)
    assists = player.get("assists", 0)
    bonus = player.get("bonus", 0)
    
    # Calculate appearances (90 minute equivalents)
    appearances = minutes_played / 90.0 if minutes_played > 0 else 0
    
    # Points per 90 minutes
    points_per_90 = round(total_points / appearances, 2) if appearances > 0 else 0
    
    # Points per million (value)
    points_per_million = round(total_points / cost, 2) if cost > 0 else 0
    
    # Points per game per million
    points_per_game_per_million = round(points_per_game / cost, 2) if cost > 0 else 0
    
    # Goals/assists per 90
    goals_per_90 = round(goals / appearances, 2) if appearances > 0 else 0
    assists_per_90 = round(assists / appearances, 2) if appearances > 0 else 0
    bonus_per_90 = round(bonus / appearances, 2) if appearances > 0 else 0
    
    return {
        "points_per_90": points_per_90,
        "points_per_million": points_per_million,
        "points_per_game_per_million": points_per_game_per_million,
        "points_per_million_per_90": round(points_per_90 / cost, 2) if cost > 0 else 0,
        "goals_per_90": goals_per_90,
        "assists_per_90": assists_per_90,
        "bonus_per_90": bonus_per_90,
        "appearances_90": round(appearances, 1),
    }


def calculate_expected_performance(player: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate expected vs actual performance metrics.
    
    Args:
        player: Raw player dict from FPL API
        
    Returns:
        Dict with xG/xA analysis
    """
    goals = player.get("goals_scored", 0)
    assists = player.get("assists", 0)
    xg = float(player.get("expected_goals", 0) or 0)
    xa = float(player.get("expected_assists", 0) or 0)
    xgi = float(player.get("expected_goal_involvements", 0) or 0)
    xgc = float(player.get("expected_goals_conceded", 0) or 0)
    goals_conceded = player.get("goals_conceded", 0)
    
    goals_vs_xg = round(goals - xg, 2)
    assists_vs_xa = round(assists - xa, 2)
    gi_vs_xgi = round((goals + assists) - xgi, 2)
    gc_vs_xgc = round(goals_conceded - xgc, 2)
    
    # Determine performance status
    if goals_vs_xg > 1.5:
        goal_status = "significantly_overperforming"
    elif goals_vs_xg > 0.5:
        goal_status = "overperforming"
    elif goals_vs_xg < -1.5:
        goal_status = "significantly_underperforming"
    elif goals_vs_xg < -0.5:
        goal_status = "underperforming"
    else:
        goal_status = "on_track"
    
    return {
        "expected_goals": xg,
        "expected_assists": xa,
        "expected_goal_involvements": xgi,
        "expected_goals_conceded": xgc,
        "goals_vs_xg": goals_vs_xg,
        "assists_vs_xa": assists_vs_xa,
        "goal_involvements_vs_xgi": gi_vs_xgi,
        "goals_conceded_vs_xgc": gc_vs_xgc,
        "performance_status": goal_status,
    }


# =============================================================================
# CLASSIFICATION UTILITIES
# =============================================================================

def classify_ownership(selected_by_percent: float) -> str:
    """
    Classify player by ownership tier.
    
    Args:
        selected_by_percent: Ownership percentage
        
    Returns:
        Tier name: "template", "popular", "differential", or "punt"
    """
    if selected_by_percent >= OWNERSHIP_TIERS["template"]:
        return "template"
    elif selected_by_percent >= OWNERSHIP_TIERS["popular"]:
        return "popular"
    elif selected_by_percent >= OWNERSHIP_TIERS["differential"]:
        return "differential"
    else:
        return "punt"


def classify_form(form: float) -> str:
    """
    Classify player by form rating.
    
    Args:
        form: Form rating
        
    Returns:
        Form tier: "excellent", "good", "average", or "poor"
    """
    if form >= FORM_THRESHOLDS["excellent"]:
        return "excellent"
    elif form >= FORM_THRESHOLDS["good"]:
        return "good"
    elif form >= FORM_THRESHOLDS["average"]:
        return "average"
    else:
        return "poor"


def classify_price(price: float) -> str:
    """
    Classify player by price tier.
    
    Args:
        price: Price in millions
        
    Returns:
        Price tier: "premium", "mid_price", "budget", or "enabler"
    """
    if price >= VALUE_THRESHOLDS["premium_min"]:
        return "premium"
    elif price >= VALUE_THRESHOLDS["mid_price_min"]:
        return "mid_price"
    elif price >= VALUE_THRESHOLDS["budget_min"]:
        return "budget"
    else:
        return "enabler"


def classify_transfer_trend(net_transfers: int) -> str:
    """
    Classify player by transfer trend.
    
    Args:
        net_transfers: Net transfers (in - out)
        
    Returns:
        Trend indicator with emoji
    """
    if net_transfers >= TRANSFER_THRESHOLDS["very_hot"]:
        return "🔥 Very Hot"
    elif net_transfers >= TRANSFER_THRESHOLDS["rising"]:
        return "📈 Rising"
    elif net_transfers <= TRANSFER_THRESHOLDS["falling_fast"]:
        return "📉 Falling Fast"
    elif net_transfers <= TRANSFER_THRESHOLDS["falling"]:
        return "⬇️ Dropping"
    else:
        return "➡️ Stable"


def classify_fixture_difficulty(difficulty: int) -> str:
    """
    Get human-readable fixture difficulty.
    
    Args:
        difficulty: FDR rating (1-5)
        
    Returns:
        Difficulty text
    """
    return FIXTURE_DIFFICULTY.get(difficulty, "Unknown")


def get_availability_text(status: str, chance: Optional[int] = None) -> str:
    """
    Get human-readable availability status.
    
    Args:
        status: Status code (a, d, i, s, n, u)
        chance: Chance of playing percentage
        
    Returns:
        Status text with percentage if available
    """
    base_status = AVAILABILITY_STATUS.get(status, "Unknown")
    if chance is not None and status != "a":
        return f"{base_status} - {chance}% chance"
    return base_status


# =============================================================================
# DATA ENRICHMENT
# =============================================================================

def enrich_player_data(
    player: Dict[str, Any],
    team: Optional[Dict[str, Any]] = None,
    live_stats: Optional[Dict[str, Any]] = None,
    include_calculated_stats: bool = True,
    include_expected_stats: bool = True,
    include_classifications: bool = True,
) -> Dict[str, Any]:
    """
    Enrich raw player data with team info, position names, and calculated stats.
    
    This is the single source of truth for player data enrichment.
    
    Args:
        player: Raw player dict from FPL API or cache
        team: Optional team dict for team name/short_name
        live_stats: Optional live gameweek stats dict
        include_calculated_stats: Whether to include PPM, points_per_90, etc.
        include_expected_stats: Whether to include xG/xA analysis
        include_classifications: Whether to include ownership/form/price tiers
        
    Returns:
        Enriched player dict
    """
    price = player.get("now_cost", 0) / 10
    form = float(player.get("form", 0) or 0)
    ownership = float(player.get("selected_by_percent", 0) or 0)
    
    enriched = {
        # Core identifiers
        "id": player.get("id"),
        "web_name": player.get("web_name", "Unknown"),
        "full_name": get_player_full_name(player),
        
        # Position
        "position": get_position_name(player.get("element_type", 0)),
        "position_full": get_position_full_name(player.get("element_type", 0)),
        "element_type": player.get("element_type"),
        
        # Pricing
        "price": price,
        "price_change_event": player.get("cost_change_event", 0) / 10,
        "price_change_start": player.get("cost_change_start", 0) / 10,
        
        # Core stats
        "form": form,
        "points_per_game": float(player.get("points_per_game", 0) or 0),
        "total_points": player.get("total_points", 0),
        "minutes": player.get("minutes", 0),
        "selected_by_percent": ownership,
        
        # Scoring stats
        "goals_scored": player.get("goals_scored", 0),
        "assists": player.get("assists", 0),
        "clean_sheets": player.get("clean_sheets", 0),
        "goals_conceded": player.get("goals_conceded", 0),
        
        # Bonus
        "bonus": player.get("bonus", 0),
        "bps": player.get("bps", 0),
        
        # ICT
        "influence": float(player.get("influence", 0) or 0),
        "creativity": float(player.get("creativity", 0) or 0),
        "threat": float(player.get("threat", 0) or 0),
        "ict_index": float(player.get("ict_index", 0) or 0),
        
        # Availability
        "status": player.get("status", "a"),
        "news": player.get("news", ""),
        "chance_of_playing_next": player.get("chance_of_playing_next_round"),
        "chance_of_playing_this": player.get("chance_of_playing_this_round"),
        "is_available": player.get("status", "a") == "a",
        "availability_text": get_availability_text(
            player.get("status", "a"),
            player.get("chance_of_playing_next_round")
        ),
        
        # Other stats
        "yellow_cards": player.get("yellow_cards", 0),
        "red_cards": player.get("red_cards", 0),
        "saves": player.get("saves", 0),
        "penalties_saved": player.get("penalties_saved", 0),
        "penalties_missed": player.get("penalties_missed", 0),
        "own_goals": player.get("own_goals", 0),
        
        # Photo
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
        enriched["gw_goals"] = live_stats.get("goals_scored", 0)
        enriched["gw_assists"] = live_stats.get("assists", 0)
        enriched["gw_bonus"] = live_stats.get("bonus", 0)
    
    # Add calculated stats if requested
    if include_calculated_stats:
        calculated = calculate_player_stats(player)
        enriched["derived_stats"] = calculated
        # Also add key metrics at top level for convenience
        enriched["points_per_90"] = calculated["points_per_90"]
        enriched["points_per_million"] = calculated["points_per_million"]
    
    # Add expected stats if requested
    if include_expected_stats:
        expected = calculate_expected_performance(player)
        enriched["expected_stats"] = expected
        # Add key xG metrics at top level
        enriched["xG"] = expected["expected_goals"]
        enriched["xA"] = expected["expected_assists"]
        enriched["xG_difference"] = expected["goals_vs_xg"]
        enriched["performance_status"] = expected["performance_status"]
    
    # Add classifications if requested
    if include_classifications:
        enriched["ownership_tier"] = classify_ownership(ownership)
        enriched["form_tier"] = classify_form(form)
        enriched["price_tier"] = classify_price(price)
        
        # Transfer trend
        net_transfers = player.get("transfers_in_event", 0) - player.get("transfers_out_event", 0)
        enriched["transfer_trend"] = classify_transfer_trend(net_transfers)
        enriched["net_transfers_event"] = net_transfers
    
    return enriched


# =============================================================================
# PARSING UTILITIES
# =============================================================================

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


# =============================================================================
# FORMATTING UTILITIES
# =============================================================================

def format_price(price: float) -> str:
    """
    Format price as £X.Xm string.
    
    Args:
        price: Price in millions
        
    Returns:
        Formatted string like "£10.5m"
    """
    return f"£{price:.1f}m"


def format_number(value: Union[int, float], decimal_places: int = 0) -> str:
    """
    Format number with comma separators.
    
    Args:
        value: Number to format
        decimal_places: Number of decimal places
        
    Returns:
        Formatted string like "1,234,567"
    """
    if decimal_places > 0:
        return f"{value:,.{decimal_places}f}"
    return f"{int(value):,}"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format value as percentage string.
    
    Args:
        value: Percentage value (e.g., 45.5)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted string like "45.5%"
    """
    return f"{value:.{decimal_places}f}%"


def format_metric_name(metric: str) -> str:
    """
    Get human-readable name for a metric.
    
    Args:
        metric: Metric key (e.g., "total_points")
        
    Returns:
        Display name (e.g., "Total Points")
    """
    return METRIC_DISPLAY_NAMES.get(metric, metric.replace("_", " ").title())


def format_timestamp(dt: datetime) -> str:
    """
    Format datetime for display.
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted string like "Dec 7, 2024 10:30 AM"
    """
    return dt.strftime("%b %d, %Y %I:%M %p")


# =============================================================================
# PLAYER SUMMARY GENERATION
# =============================================================================

def generate_player_summary(player: Dict[str, Any], include_fixtures: bool = False) -> str:
    """
    Generate a concise text summary of a player for LLM context.
    
    Args:
        player: Enriched player dict
        include_fixtures: Whether to include upcoming fixtures
        
    Returns:
        Formatted text summary
    """
    lines = [
        f"{player.get('web_name', 'Unknown')} ({player.get('team_short', 'UNK')}, {player.get('position', 'UNK')}) - {format_price(player.get('price', 0))}",
        f"  Points: {player.get('total_points', 0)} | Form: {player.get('form', 0)} | Owned: {format_percentage(player.get('selected_by_percent', 0))}",
    ]
    
    # Add scoring stats if relevant
    goals = player.get('goals_scored', 0)
    assists = player.get('assists', 0)
    if goals or assists:
        lines.append(f"  Goals: {goals} | Assists: {assists}")
    
    # Add xG analysis if available
    if player.get('expected_stats'):
        xg_diff = player.get('xG_difference', 0)
        status = player.get('performance_status', 'on_track')
        status_emoji = "✅" if "over" in status else "⚠️" if "under" in status else "➡️"
        lines.append(f"  xG: {player.get('xG', 0):.2f} | xA: {player.get('xA', 0):.2f} | {status_emoji} {status.replace('_', ' ').title()}")
    
    # Add derived stats if available
    if player.get('derived_stats'):
        ppm = player.get('points_per_million', 0)
        pp90 = player.get('points_per_90', 0)
        lines.append(f"  Value: {ppm:.1f} pts/£m | {pp90:.1f} pts/90")
    
    # Add availability if flagged
    if not player.get('is_available', True) or player.get('news'):
        lines.append(f"  ⚠️ {player.get('availability_text', player.get('news', 'Flagged'))}")
    
    # Add transfer trend
    if player.get('transfer_trend'):
        lines.append(f"  Transfers: {player.get('transfer_trend')} ({format_number(player.get('net_transfers_event', 0))} net)")
    
    # Add fixtures if requested
    if include_fixtures and player.get('upcoming_fixtures'):
        fixtures = player.get('upcoming_fixtures', [])[:3]
        fixtures_str = ", ".join(
            f"GW{f.get('gameweek')}: {f.get('opponent')}({f.get('venue')})"
            for f in fixtures
        )
        lines.append(f"  Fixtures: {fixtures_str}")
    
    return "\n".join(lines)

