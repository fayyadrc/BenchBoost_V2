"""
Context Builder for LLM-Optimized Data Summaries

Prepares concise, formatted context from FPL data to minimize token usage
while maximizing information density for the LLM.
"""

from typing import List, Dict, Any, Optional
import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(project_root)

from backend.data import cache


def build_player_context(player_names: List[str]) -> str:
    """
    Build concise player context for LLM.
    
    Args:
        player_names: List of player names to include
        
    Returns:
        Formatted string with essential player info
    """
    if not player_names:
        return "No players specified."
    
    context_lines = ["Player Information:"]
    
    for name in player_names:
        player = cache.get_player_by_name(name)
        
        if not player:
            context_lines.append(f"  • {name}: Not found")
            continue
        
        # Get team name
        team = cache.get_team_by_id(player.get("team"))
        team_name = team.get("short_name", "Unknown") if team else "Unknown"
        
        # Format position
        position_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}
        position = position_map.get(player.get("element_type"), "Unknown")
        
        # Build concise summary
        context_lines.append(
            f"  • {player.get('web_name')} ({team_name}, {position}) - "
            f"£{player.get('now_cost', 0) / 10:.1f}m, "
            f"{player.get('total_points', 0)}pts, "
            f"Form: {player.get('form', 'N/A')}, "
            f"Owned: {player.get('selected_by_percent', 0)}%"
        )
    
    return "\n".join(context_lines)


def build_player_comparison(player_names: List[str], sort_by: str = "total_points") -> str:
    """
    Build a comparison table of players.
    
    Args:
        player_names: List of player names to compare
        sort_by: Metric to sort by (total_points, form, now_cost, etc.)
        
    Returns:
        Formatted comparison string
    """
    if not player_names:
        return "No players to compare."
    
    players = []
    for name in player_names:
        player = cache.get_player_by_name(name)
        if player:
            players.append(player)
    
    if not players:
        return "None of the specified players were found."
    
    # Sort players
    players.sort(key=lambda p: p.get(sort_by, 0), reverse=True)
    
    # Build comparison
    lines = [f"Player Comparison (sorted by {sort_by}):"]
    lines.append("-" * 60)
    
    for player in players:
        team = cache.get_team_by_id(player.get("team"))
        team_name = team.get("short_name", "???") if team else "???"
        
        lines.append(
            f"{player.get('web_name'):15} | {team_name:3} | "
            f"£{player.get('now_cost', 0) / 10:4.1f}m | "
            f"{player.get('total_points', 0):3}pts | "
            f"Form: {player.get('form', 'N/A'):4}"
        )
    
    return "\n".join(lines)


def build_fixture_difficulty_narrative(team_name: str, num_fixtures: int = 5) -> str:
    """
    Build a narrative about a team's upcoming fixture difficulty.
    
    Args:
        team_name: Name of the team
        num_fixtures: Number of upcoming fixtures to analyze
        
    Returns:
        Formatted fixture difficulty narrative
    """
    team = cache.get_team_by_name(team_name)
    
    if not team:
        return f"Team '{team_name}' not found."
    
    team_id = team.get("id")
    
    # Get all fixtures for this team
    all_fixtures = cache.core_data.get("fixtures", {}).values()
    team_fixtures = [
        f for f in all_fixtures
        if (f.get("team_h") == team_id or f.get("team_a") == team_id)
        and not f.get("finished", False)
    ]
    
    # Sort by kickoff time and take next N
    team_fixtures.sort(key=lambda f: f.get("kickoff_time", ""))
    upcoming = team_fixtures[:num_fixtures]
    
    if not upcoming:
        return f"{team.get('name')} has no upcoming fixtures."
    
    lines = [f"Upcoming Fixtures for {team.get('name')}:"]
    
    for fixture in upcoming:
        is_home = fixture.get("team_h") == team_id
        opponent_id = fixture.get("team_a") if is_home else fixture.get("team_h")
        opponent = cache.get_team_by_id(opponent_id)
        opponent_name = opponent.get("short_name", "???") if opponent else "???"
        
        # Get difficulty rating
        difficulty = fixture.get("team_h_difficulty" if is_home else "team_a_difficulty", 0)
        difficulty_text = ["Very Easy", "Easy", "Medium", "Hard", "Very Hard"][min(difficulty - 1, 4)] if difficulty > 0 else "Unknown"
        
        venue = "H" if is_home else "A"
        gameweek = fixture.get("event", "?")
        
        lines.append(f"  GW{gameweek}: vs {opponent_name} ({venue}) - Difficulty: {difficulty_text} ({difficulty}/5)")
    
    return "\n".join(lines)


def build_team_summary(team_name: str) -> str:
    """
    Build a summary of a team's key information.
    
    Args:
        team_name: Name of the team
        
    Returns:
        Formatted team summary
    """
    team = cache.get_team_by_name(team_name)
    
    if not team:
        return f"Team '{team_name}' not found."
    
    lines = [
        f"Team: {team.get('name')} ({team.get('short_name')})",
        f"  Strength Overall: {team.get('strength', 0)}",
        f"  Strength Attack (H/A): {team.get('strength_attack_home', 0)}/{team.get('strength_attack_away', 0)}",
        f"  Strength Defence (H/A): {team.get('strength_defence_home', 0)}/{team.get('strength_defence_away', 0)}",
        f"  Position: {team.get('position', 'N/A')}",
    ]
    
    return "\n".join(lines)


def build_gameweek_summary(gameweek_id: Optional[int] = None) -> str:
    """
    Build a summary of gameweek information.
    
    Args:
        gameweek_id: Specific gameweek ID, or None for current gameweek
        
    Returns:
        Formatted gameweek summary
    """
    if gameweek_id is None:
        gw = cache.get_current_gameweek()
        if not gw:
            return "No current gameweek found."
    else:
        gw = cache.get_gameweek_by_id(gameweek_id)
        if not gw:
            return f"Gameweek {gameweek_id} not found."
    
    lines = [
        f"Gameweek {gw.get('id')}: {gw.get('name')}",
        f"  Deadline: {gw.get('deadline_time')}",
        f"  Status: {'Finished' if gw.get('finished') else 'In Progress' if gw.get('is_current') else 'Upcoming'}",
    ]
    
    if gw.get("finished"):
        lines.extend([
            f"  Average Score: {gw.get('average_entry_score', 'N/A')}",
            f"  Highest Score: {gw.get('highest_score', 'N/A')}",
        ])
    
    # Add chip plays if available
    chip_plays = gw.get("chip_plays", [])
    if chip_plays:
        lines.append("  Chips Played:")
        for chip in chip_plays:
            lines.append(f"    - {chip.get('chip_name')}: {chip.get('num_played'):,} times")
    
    return "\n".join(lines)


def build_top_players_summary(
    position: Optional[str] = None,
    metric: str = "total_points",
    count: int = 10
) -> str:
    """
    Build a summary of top players by a specific metric.
    
    Args:
        position: Filter by position (GK, DEF, MID, FWD) or None for all
        metric: Metric to sort by (total_points, form, selected_by_percent, etc.)
        count: Number of players to include
        
    Returns:
        Formatted top players summary
    """
    all_players = list(cache.core_data.get("players", {}).values())
    
    # Check if cache has any players loaded
    if not all_players:
        return "No player data available. The cache may not be loaded yet. Please try refreshing the data."
    
    # Filter by position if specified
    if position:
        position_map = {"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}
        position_id = position_map.get(position.upper())
        if position_id:
            all_players = [p for p in all_players if p.get("element_type") == position_id]
        else:
            return f"Invalid position '{position}'. Valid positions are: GK, DEF, MID, FWD"
    
    # Check if any players match the filter
    if not all_players:
        position_text = f"{position} " if position else ""
        return f"No {position_text}players found in the data."
    
    # Sort by metric
    all_players.sort(key=lambda p: float(p.get(metric, 0)), reverse=True)
    top_players = all_players[:count]
    
    position_text = f"{position} " if position else ""
    lines = [f"Top {count} {position_text}Players by {metric}:"]
    lines.append("-" * 70)
    
    for i, player in enumerate(top_players, 1):
        team = cache.get_team_by_id(player.get("team"))
        team_name = team.get("short_name", "???") if team else "???"
        
        lines.append(
            f"{i:2}. {player.get('web_name'):15} ({team_name:3}) - "
            f"£{player.get('now_cost', 0) / 10:4.1f}m | "
            f"{metric}: {player.get(metric, 0)}"
        )
    
    return "\n".join(lines)
