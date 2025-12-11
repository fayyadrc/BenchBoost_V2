"""
Advanced FPL Tools

Provides specialized analysis tools:
- Captain Recommendations
- Fixture Difficulty Analyzer  
- Double/Blank Gameweek Detection
- Player Watchlist Management
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
import json
import os

from .api_client import bootstrap_static, fixtures, element_summary, DEFAULT_TIMEOUT
from .cache import (
    load_core_game_data, 
    core_data, 
    get_player_by_name, 
    get_player_by_id,
    get_team_by_id, 
    get_team_by_name,
    get_current_gameweek,
    get_upcoming_fixtures_for_team,
)
from .utils import (
    enrich_player_data,
    classify_fixture_difficulty,
    format_price,
    format_percentage,
    get_position_name,
)
from .constants import (
    FIXTURE_DIFFICULTY,
    FIXTURE_THRESHOLDS,
    POSITION_ID_TO_NAME,
)


# =============================================================================
# CAPTAIN RECOMMENDATIONS
# =============================================================================

@dataclass
class CaptainCandidate:
    """A player being considered for captaincy."""
    player_id: int
    web_name: str
    full_name: str
    team_name: str
    team_short: str
    position: str
    price: float
    
    # Current performance
    form: float
    total_points: int
    points_per_game: float
    
    # Fixture info
    fixture_difficulty: int
    opponent: str
    is_home: bool
    
    # Expected stats
    xG: float = 0.0
    xA: float = 0.0
    xGI: float = 0.0
    
    # Scoring
    captain_score: float = 0.0
    reasoning: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_captain_recommendations(
    entry_id: Optional[int] = None,
    gameweek: Optional[int] = None,
    count: int = 5,
    include_differentials: bool = True,
) -> Dict[str, Any]:
    """
    Get captain recommendations based on form, fixtures, and expected stats.
    
    Args:
        entry_id: Optional manager ID to prioritize their squad players
        gameweek: Gameweek to analyze (defaults to current/next)
        count: Number of recommendations to return
        include_differentials: Include low-ownership differential picks
        
    Returns:
        Dict with top_picks, differential_picks, and analysis
    """
    # Ensure data is loaded
    load_core_game_data()
    
    # Determine target gameweek
    current_gw = get_current_gameweek()
    if not current_gw:
        return {"error": "Could not determine current gameweek"}
    
    target_gw = gameweek or (current_gw["id"] if not current_gw.get("finished") else current_gw["id"] + 1)
    
    # Get all fixtures for target gameweek
    gw_fixtures = [
        f for f in core_data.get("fixtures", {}).values()
        if f.get("event") == target_gw
    ]
    
    if not gw_fixtures:
        return {"error": f"No fixtures found for gameweek {target_gw}"}
    
    # Build team -> fixture mapping
    team_fixtures = {}
    for fixture in gw_fixtures:
        team_h = fixture.get("team_h")
        team_a = fixture.get("team_a")
        opponent_h = get_team_by_id(team_a)
        opponent_a = get_team_by_id(team_h)
        
        team_fixtures[team_h] = {
            "opponent_id": team_a,
            "opponent": opponent_h.get("short_name", "UNK") if opponent_h else "UNK",
            "opponent_full": opponent_h.get("name", "Unknown") if opponent_h else "Unknown",
            "is_home": True,
            "difficulty": fixture.get("team_h_difficulty", 3),
        }
        team_fixtures[team_a] = {
            "opponent_id": team_h,
            "opponent": opponent_a.get("short_name", "UNK") if opponent_a else "UNK",
            "opponent_full": opponent_a.get("name", "Unknown") if opponent_a else "Unknown",
            "is_home": False,
            "difficulty": fixture.get("team_a_difficulty", 3),
        }
    
    # Get manager's squad if entry_id provided
    manager_squad_ids = set()
    if entry_id:
        try:
            from .manager_data import get_manager_squad_data
            squad = get_manager_squad_data(entry_id, target_gw)
            if squad and "starting_xi" in squad:
                for player in squad.get("starting_xi", []) + squad.get("bench", []):
                    manager_squad_ids.add(player.get("element"))
        except Exception:
            pass  # Manager squad is optional enhancement
    
    # Score all eligible players
    candidates = []
    
    for player_id, player in core_data.get("players", {}).items():
        # Skip unavailable players
        if player.get("status") in ["u", "i", "s"]:  # unavailable, injured, suspended
            continue
        
        # Skip players with very low minutes (bench warmers)
        if player.get("minutes", 0) < 180:
            continue
        
        team_id = player.get("team")
        if team_id not in team_fixtures:
            continue  # Team has no fixture (blank GW)
        
        fixture_info = team_fixtures[team_id]
        team = get_team_by_id(team_id)
        
        # Calculate captain score
        form = float(player.get("form", 0) or 0)
        ppg = float(player.get("points_per_game", 0) or 0)
        xg = float(player.get("expected_goals", 0) or 0)
        xa = float(player.get("expected_assists", 0) or 0)
        xgi = float(player.get("expected_goal_involvements", 0) or 0)
        ict = float(player.get("ict_index", 0) or 0)
        ownership = float(player.get("selected_by_percent", 0) or 0)
        difficulty = fixture_info["difficulty"]
        is_home = fixture_info["is_home"]
        
        # Build scoring components
        score = 0
        reasoning = []
        risks = []
        
        # Form weight (40% of score)
        form_score = form * 4
        score += form_score
        if form >= 6:
            reasoning.append(f"Excellent form ({form})")
        elif form >= 4:
            reasoning.append(f"Good form ({form})")
        elif form < 2:
            risks.append(f"Poor form ({form})")
        
        # PPG weight (20% of score)
        ppg_score = ppg * 2
        score += ppg_score
        if ppg >= 6:
            reasoning.append(f"High PPG ({ppg})")
        
        # Fixture difficulty weight (25% of score)
        # Lower difficulty = higher score
        fixture_score = (6 - difficulty) * 5
        score += fixture_score
        if difficulty <= 2:
            reasoning.append(f"Easy fixture vs {fixture_info['opponent']} ({classify_fixture_difficulty(difficulty)})")
        elif difficulty >= 4:
            risks.append(f"Tough fixture vs {fixture_info['opponent']} ({classify_fixture_difficulty(difficulty)})")
        
        # Home advantage (5%)
        if is_home:
            score += 2.5
            reasoning.append("Home fixture")
        
        # xGI weight (10%)
        minutes = player.get("minutes", 0)
        if minutes > 0:
            xgi_per_90 = (xgi / (minutes / 90)) if minutes > 90 else xgi
            xgi_score = xgi_per_90 * 5
            score += xgi_score
            if xgi_per_90 >= 0.5:
                reasoning.append(f"High xGI ({xgi:.2f})")
        
        # Bonus for being in manager's squad
        if player_id in manager_squad_ids:
            score += 5  # Small boost for owned players
        
        # Create candidate
        candidate = CaptainCandidate(
            player_id=player_id,
            web_name=player.get("web_name", "Unknown"),
            full_name=f"{player.get('first_name', '')} {player.get('second_name', '')}".strip(),
            team_name=team.get("name", "Unknown") if team else "Unknown",
            team_short=team.get("short_name", "UNK") if team else "UNK",
            position=POSITION_ID_TO_NAME.get(player.get("element_type", 0), "UNK"),
            price=player.get("now_cost", 0) / 10,
            form=form,
            total_points=player.get("total_points", 0),
            points_per_game=ppg,
            fixture_difficulty=difficulty,
            opponent=fixture_info["opponent"],
            is_home=is_home,
            xG=xg,
            xA=xa,
            xGI=xgi,
            captain_score=round(score, 2),
            reasoning=reasoning,
            risks=risks,
        )
        
        candidates.append(candidate)
    
    # Sort by captain score
    candidates.sort(key=lambda x: x.captain_score, reverse=True)
    
    # Get top picks
    top_picks = candidates[:count]
    
    # Get differential picks (low ownership)
    differential_picks = []
    if include_differentials:
        for c in candidates:
            player = get_player_by_id(c.player_id)
            if player:
                ownership = float(player.get("selected_by_percent", 0) or 0)
                if ownership < 15 and c.captain_score >= 30:  # Decent score but low owned
                    differential_picks.append(c)
                    if len(differential_picks) >= 3:
                        break
    
    return {
        "gameweek": target_gw,
        "top_picks": [c.to_dict() for c in top_picks],
        "differential_picks": [c.to_dict() for c in differential_picks],
        "analysis": {
            "total_candidates_analyzed": len(candidates),
            "fixtures_count": len(gw_fixtures),
            "manager_squad_boost_applied": bool(manager_squad_ids),
        },
        "_meta": {
            "fetched_at": datetime.now().isoformat(),
            "source": "captain_analyzer",
        }
    }


# =============================================================================
# FIXTURE DIFFICULTY ANALYZER
# =============================================================================

@dataclass
class TeamFixtureRun:
    """Analysis of a team's upcoming fixture difficulty."""
    team_id: int
    team_name: str
    team_short: str
    
    fixtures: List[Dict[str, Any]] = field(default_factory=list)
    average_difficulty: float = 0.0
    easy_fixtures: int = 0      # Difficulty 1-2
    medium_fixtures: int = 0    # Difficulty 3
    hard_fixtures: int = 0      # Difficulty 4-5
    home_fixtures: int = 0
    away_fixtures: int = 0
    
    fixture_rating: str = "Medium"  # Easy, Medium, Hard
    recommendation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def analyze_fixture_difficulty(
    num_gameweeks: int = 6,
    sort_by: str = "easiest",
) -> Dict[str, Any]:
    """
    Analyze fixture difficulty for all teams over upcoming gameweeks.
    
    Args:
        num_gameweeks: Number of gameweeks to analyze
        sort_by: "easiest" or "hardest" to sort teams
        
    Returns:
        Dict with team fixture runs, sorted by difficulty
    """
    load_core_game_data()
    
    current_gw = get_current_gameweek()
    if not current_gw:
        return {"error": "Could not determine current gameweek"}
    
    start_gw = current_gw["id"] if not current_gw.get("finished") else current_gw["id"] + 1
    end_gw = start_gw + num_gameweeks
    
    # Get all fixtures in range
    relevant_fixtures = [
        f for f in core_data.get("fixtures", {}).values()
        if f.get("event") is not None and start_gw <= f.get("event") < end_gw
    ]
    
    # Build team fixture runs
    team_runs = {}
    
    for team_id, team in core_data.get("teams", {}).items():
        team_runs[team_id] = TeamFixtureRun(
            team_id=team_id,
            team_name=team.get("name", "Unknown"),
            team_short=team.get("short_name", "UNK"),
        )
    
    # Process each fixture
    for fixture in relevant_fixtures:
        team_h = fixture.get("team_h")
        team_a = fixture.get("team_a")
        gw = fixture.get("event")
        
        opponent_h = get_team_by_id(team_a)
        opponent_a = get_team_by_id(team_h)
        
        diff_h = fixture.get("team_h_difficulty", 3)
        diff_a = fixture.get("team_a_difficulty", 3)
        
        # Home team fixture
        if team_h in team_runs:
            team_runs[team_h].fixtures.append({
                "gameweek": gw,
                "opponent": opponent_h.get("short_name", "UNK") if opponent_h else "UNK",
                "opponent_full": opponent_h.get("name", "Unknown") if opponent_h else "Unknown",
                "is_home": True,
                "difficulty": diff_h,
                "difficulty_text": classify_fixture_difficulty(diff_h),
            })
            team_runs[team_h].home_fixtures += 1
            if diff_h <= 2:
                team_runs[team_h].easy_fixtures += 1
            elif diff_h == 3:
                team_runs[team_h].medium_fixtures += 1
            else:
                team_runs[team_h].hard_fixtures += 1
        
        # Away team fixture
        if team_a in team_runs:
            team_runs[team_a].fixtures.append({
                "gameweek": gw,
                "opponent": opponent_a.get("short_name", "UNK") if opponent_a else "UNK",
                "opponent_full": opponent_a.get("name", "Unknown") if opponent_a else "Unknown",
                "is_home": False,
                "difficulty": diff_a,
                "difficulty_text": classify_fixture_difficulty(diff_a),
            })
            team_runs[team_a].away_fixtures += 1
            if diff_a <= 2:
                team_runs[team_a].easy_fixtures += 1
            elif diff_a == 3:
                team_runs[team_a].medium_fixtures += 1
            else:
                team_runs[team_a].hard_fixtures += 1
    
    # Calculate averages and ratings
    results = []
    for team_id, run in team_runs.items():
        if not run.fixtures:
            continue
        
        # Sort fixtures by gameweek
        run.fixtures.sort(key=lambda x: x["gameweek"])
        
        # Calculate average difficulty
        total_diff = sum(f["difficulty"] for f in run.fixtures)
        run.average_difficulty = round(total_diff / len(run.fixtures), 2)
        
        # Determine rating
        if run.average_difficulty <= FIXTURE_THRESHOLDS["easy_max"]:
            run.fixture_rating = "Easy"
            run.recommendation = "Good time to target players from this team"
        elif run.average_difficulty <= FIXTURE_THRESHOLDS["medium_max"]:
            run.fixture_rating = "Medium"
            run.recommendation = "Mixed fixtures - consider form over fixtures"
        else:
            run.fixture_rating = "Hard"
            run.recommendation = "Consider avoiding or selling players from this team"
        
        results.append(run)
    
    # Sort by difficulty
    if sort_by == "easiest":
        results.sort(key=lambda x: x.average_difficulty)
    else:
        results.sort(key=lambda x: x.average_difficulty, reverse=True)
    
    # Categorize teams
    easy_teams = [r for r in results if r.fixture_rating == "Easy"]
    medium_teams = [r for r in results if r.fixture_rating == "Medium"]
    hard_teams = [r for r in results if r.fixture_rating == "Hard"]
    
    return {
        "gameweek_range": f"GW{start_gw} - GW{end_gw - 1}",
        "num_gameweeks": num_gameweeks,
        "all_teams": [r.to_dict() for r in results],
        "easy_runs": [r.to_dict() for r in easy_teams[:5]],
        "hard_runs": [r.to_dict() for r in hard_teams[:5]],
        "summary": {
            "teams_with_easy_run": len(easy_teams),
            "teams_with_medium_run": len(medium_teams),
            "teams_with_hard_run": len(hard_teams),
        },
        "_meta": {
            "fetched_at": datetime.now().isoformat(),
            "source": "fixture_analyzer",
        }
    }


def get_team_fixture_analysis(team_name: str, num_gameweeks: int = 8) -> Dict[str, Any]:
    """
    Get detailed fixture analysis for a specific team.
    
    Args:
        team_name: Team name or short name
        num_gameweeks: Number of gameweeks to analyze
        
    Returns:
        Detailed fixture analysis for the team
    """
    load_core_game_data()
    
    team = get_team_by_name(team_name)
    if not team:
        return {"error": f"Team '{team_name}' not found"}
    
    team_id = team.get("id")
    
    # Get full fixture analysis
    analysis = analyze_fixture_difficulty(num_gameweeks=num_gameweeks)
    
    # Find this team's run
    team_run = None
    for t in analysis.get("all_teams", []):
        if t.get("team_id") == team_id:
            team_run = t
            break
    
    if not team_run:
        return {"error": f"No fixture data found for {team_name}"}
    
    # Get key players from this team
    key_players = []
    for player in core_data.get("players", {}).values():
        if player.get("team") == team_id and player.get("minutes", 0) >= 270:
            key_players.append({
                "web_name": player.get("web_name"),
                "position": POSITION_ID_TO_NAME.get(player.get("element_type", 0), "UNK"),
                "total_points": player.get("total_points", 0),
                "form": float(player.get("form", 0) or 0),
                "price": player.get("now_cost", 0) / 10,
            })
    
    # Sort by total points
    key_players.sort(key=lambda x: x["total_points"], reverse=True)
    
    return {
        "team": team.get("name"),
        "team_short": team.get("short_name"),
        "fixture_run": team_run,
        "key_players": key_players[:5],
        "recommendation": team_run.get("recommendation"),
        "_meta": {
            "fetched_at": datetime.now().isoformat(),
            "source": "team_fixture_analyzer",
        }
    }


# =============================================================================
# DOUBLE/BLANK GAMEWEEK DETECTION
# =============================================================================

def detect_dgw_bgw(num_gameweeks: int = 10) -> Dict[str, Any]:
    """
    Detect Double Gameweeks (DGW) and Blank Gameweeks (BGW).
    
    A DGW occurs when a team plays twice in one gameweek.
    A BGW occurs when a team doesn't play in a gameweek.
    
    Args:
        num_gameweeks: Number of upcoming gameweeks to check
        
    Returns:
        Dict with DGW and BGW information
    """
    load_core_game_data()
    
    current_gw = get_current_gameweek()
    if not current_gw:
        return {"error": "Could not determine current gameweek"}
    
    start_gw = current_gw["id"] if not current_gw.get("finished") else current_gw["id"] + 1
    end_gw = start_gw + num_gameweeks
    
    # Track fixtures per team per gameweek
    team_gw_fixtures = {}  # {team_id: {gw: count}}
    
    for team_id in core_data.get("teams", {}).keys():
        team_gw_fixtures[team_id] = {gw: 0 for gw in range(start_gw, end_gw)}
    
    # Count fixtures
    for fixture in core_data.get("fixtures", {}).values():
        gw = fixture.get("event")
        if gw is None or gw < start_gw or gw >= end_gw:
            continue
        
        team_h = fixture.get("team_h")
        team_a = fixture.get("team_a")
        
        if team_h in team_gw_fixtures:
            team_gw_fixtures[team_h][gw] += 1
        if team_a in team_gw_fixtures:
            team_gw_fixtures[team_a][gw] += 1
    
    # Identify DGWs and BGWs
    dgw_teams = {}  # {gw: [teams with 2+ fixtures]}
    bgw_teams = {}  # {gw: [teams with 0 fixtures]}
    
    for team_id, gw_counts in team_gw_fixtures.items():
        team = get_team_by_id(team_id)
        team_name = team.get("short_name", "UNK") if team else "UNK"
        team_full = team.get("name", "Unknown") if team else "Unknown"
        
        for gw, count in gw_counts.items():
            if count >= 2:  # Double gameweek
                if gw not in dgw_teams:
                    dgw_teams[gw] = []
                dgw_teams[gw].append({
                    "team_id": team_id,
                    "team_name": team_full,
                    "team_short": team_name,
                    "fixtures": count,
                })
            elif count == 0:  # Blank gameweek
                if gw not in bgw_teams:
                    bgw_teams[gw] = []
                bgw_teams[gw].append({
                    "team_id": team_id,
                    "team_name": team_full,
                    "team_short": team_name,
                })
    
    # Build DGW details with fixtures
    dgw_details = []
    for gw, teams in sorted(dgw_teams.items()):
        gw_fixtures = [
            f for f in core_data.get("fixtures", {}).values()
            if f.get("event") == gw
        ]
        
        for team_info in teams:
            team_id = team_info["team_id"]
            team_fixtures = []
            
            for fixture in gw_fixtures:
                if fixture.get("team_h") == team_id:
                    opponent = get_team_by_id(fixture.get("team_a"))
                    team_fixtures.append({
                        "opponent": opponent.get("short_name", "UNK") if opponent else "UNK",
                        "is_home": True,
                        "difficulty": fixture.get("team_h_difficulty", 3),
                    })
                elif fixture.get("team_a") == team_id:
                    opponent = get_team_by_id(fixture.get("team_h"))
                    team_fixtures.append({
                        "opponent": opponent.get("short_name", "UNK") if opponent else "UNK",
                        "is_home": False,
                        "difficulty": fixture.get("team_a_difficulty", 3),
                    })
            
            dgw_details.append({
                "gameweek": gw,
                **team_info,
                "fixtures_detail": team_fixtures,
            })
    
    # Build BGW details
    bgw_details = []
    for gw, teams in sorted(bgw_teams.items()):
        for team_info in teams:
            bgw_details.append({
                "gameweek": gw,
                **team_info,
            })
    
    # Get key players from DGW teams
    dgw_players = []
    if dgw_details:
        dgw_team_ids = set(d["team_id"] for d in dgw_details)
        for player in core_data.get("players", {}).values():
            if player.get("team") in dgw_team_ids and player.get("minutes", 0) >= 270:
                team = get_team_by_id(player.get("team"))
                dgw_players.append({
                    "web_name": player.get("web_name"),
                    "team_short": team.get("short_name", "UNK") if team else "UNK",
                    "position": POSITION_ID_TO_NAME.get(player.get("element_type", 0), "UNK"),
                    "total_points": player.get("total_points", 0),
                    "form": float(player.get("form", 0) or 0),
                    "price": player.get("now_cost", 0) / 10,
                })
        dgw_players.sort(key=lambda x: x["form"], reverse=True)
    
    return {
        "gameweek_range": f"GW{start_gw} - GW{end_gw - 1}",
        "has_dgw": bool(dgw_details),
        "has_bgw": bool(bgw_details),
        "double_gameweeks": dgw_details,
        "blank_gameweeks": bgw_details,
        "dgw_players_to_target": dgw_players[:10],
        "summary": {
            "total_dgw_teams": len(dgw_details),
            "total_bgw_teams": len(bgw_details),
            "dgw_gameweeks": list(dgw_teams.keys()),
            "bgw_gameweeks": list(bgw_teams.keys()),
        },
        "chip_advice": _get_chip_advice(dgw_details, bgw_details),
        "_meta": {
            "fetched_at": datetime.now().isoformat(),
            "source": "dgw_bgw_detector",
        }
    }


def _get_chip_advice(dgw_details: List, bgw_details: List) -> Dict[str, str]:
    """Generate chip usage advice based on DGW/BGW."""
    advice = {}
    
    if dgw_details:
        dgw_gws = sorted(set(d["gameweek"] for d in dgw_details))
        num_dgw_teams = len(dgw_details)
        
        if num_dgw_teams >= 4:
            advice["bench_boost"] = f"Consider Bench Boost in GW{dgw_gws[0]} - {num_dgw_teams} teams doubling"
            advice["triple_captain"] = f"Triple Captain could be effective on a premium DGW player"
        else:
            advice["bench_boost"] = f"Wait for a bigger DGW with more teams for Bench Boost"
    
    if bgw_details:
        bgw_gws = sorted(set(d["gameweek"] for d in bgw_details))
        num_bgw_teams = len(set(d["team_id"] for d in bgw_details))
        
        if num_bgw_teams >= 4:
            advice["free_hit"] = f"Free Hit could be valuable in GW{bgw_gws[0]} - {num_bgw_teams} teams blanking"
        else:
            advice["free_hit"] = "Save Free Hit for a larger blank gameweek"
    
    if not advice:
        advice["general"] = "No significant DGW/BGW detected in the near future - hold chips"
    
    return advice


# =============================================================================
# WATCHLIST MANAGEMENT
# =============================================================================

# Watchlist storage location
WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "watchlist.json")


@dataclass
class WatchlistPlayer:
    """A player on the watchlist."""
    player_id: int
    web_name: str
    team_short: str
    position: str
    price_when_added: float
    added_at: str
    notes: str = ""
    target_price: Optional[float] = None
    alert_on_price_drop: bool = False
    alert_on_price_rise: bool = False


def _load_watchlist() -> Dict[str, Any]:
    """Load watchlist from file."""
    try:
        if os.path.exists(WATCHLIST_FILE):
            with open(WATCHLIST_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {"players": [], "created_at": datetime.now().isoformat()}


def _save_watchlist(watchlist: Dict[str, Any]) -> None:
    """Save watchlist to file."""
    try:
        watchlist["updated_at"] = datetime.now().isoformat()
        with open(WATCHLIST_FILE, "w") as f:
            json.dump(watchlist, f, indent=2)
    except Exception as e:
        raise Exception(f"Failed to save watchlist: {e}")


def add_to_watchlist(
    player_name: str,
    notes: str = "",
    target_price: Optional[float] = None,
    alert_on_price_drop: bool = False,
    alert_on_price_rise: bool = False,
) -> Dict[str, Any]:
    """
    Add a player to the watchlist.
    
    Args:
        player_name: Player name to add
        notes: Optional notes about why you're watching
        target_price: Target price to buy at
        alert_on_price_drop: Set alert for price drops
        alert_on_price_rise: Set alert for price rises
        
    Returns:
        Confirmation with player details
    """
    load_core_game_data()
    
    player = get_player_by_name(player_name)
    if not player:
        return {"error": f"Player '{player_name}' not found"}
    
    player_id = player.get("id")
    team = get_team_by_id(player.get("team"))
    
    watchlist = _load_watchlist()
    
    # Check if already on watchlist
    for p in watchlist["players"]:
        if p.get("player_id") == player_id:
            return {
                "error": f"{player.get('web_name')} is already on your watchlist",
                "existing_entry": p,
            }
    
    # Add to watchlist
    entry = {
        "player_id": player_id,
        "web_name": player.get("web_name"),
        "full_name": f"{player.get('first_name', '')} {player.get('second_name', '')}".strip(),
        "team_short": team.get("short_name", "UNK") if team else "UNK",
        "position": POSITION_ID_TO_NAME.get(player.get("element_type", 0), "UNK"),
        "price_when_added": player.get("now_cost", 0) / 10,
        "added_at": datetime.now().isoformat(),
        "notes": notes,
        "target_price": target_price,
        "alert_on_price_drop": alert_on_price_drop,
        "alert_on_price_rise": alert_on_price_rise,
    }
    
    watchlist["players"].append(entry)
    _save_watchlist(watchlist)
    
    return {
        "success": True,
        "message": f"Added {player.get('web_name')} to watchlist",
        "player": entry,
        "_meta": {
            "action": "add",
            "timestamp": datetime.now().isoformat(),
        }
    }


def remove_from_watchlist(player_name: str) -> Dict[str, Any]:
    """
    Remove a player from the watchlist.
    
    Args:
        player_name: Player name to remove
        
    Returns:
        Confirmation
    """
    load_core_game_data()
    
    player = get_player_by_name(player_name)
    if not player:
        return {"error": f"Player '{player_name}' not found"}
    
    player_id = player.get("id")
    watchlist = _load_watchlist()
    
    # Find and remove
    original_count = len(watchlist["players"])
    watchlist["players"] = [p for p in watchlist["players"] if p.get("player_id") != player_id]
    
    if len(watchlist["players"]) == original_count:
        return {"error": f"{player.get('web_name')} is not on your watchlist"}
    
    _save_watchlist(watchlist)
    
    return {
        "success": True,
        "message": f"Removed {player.get('web_name')} from watchlist",
        "_meta": {
            "action": "remove",
            "timestamp": datetime.now().isoformat(),
        }
    }


def get_watchlist() -> Dict[str, Any]:
    """
    Get the current watchlist with updated player data.
    
    Returns:
        Watchlist with current prices, form, and price changes
    """
    load_core_game_data()
    
    watchlist = _load_watchlist()
    enriched_players = []
    
    price_alerts = []
    
    for entry in watchlist.get("players", []):
        player_id = entry.get("player_id")
        player = get_player_by_id(player_id)
        
        if not player:
            # Player no longer exists (transferred out)
            enriched_players.append({
                **entry,
                "status": "unavailable",
                "current_price": None,
                "price_change": None,
            })
            continue
        
        team = get_team_by_id(player.get("team"))
        current_price = player.get("now_cost", 0) / 10
        price_when_added = entry.get("price_when_added", current_price)
        price_change = round(current_price - price_when_added, 1)
        
        # Check for price alerts
        target_price = entry.get("target_price")
        if target_price and current_price <= target_price:
            price_alerts.append({
                "player": player.get("web_name"),
                "alert": f"Price dropped to £{current_price}m (target: £{target_price}m)",
            })
        
        if entry.get("alert_on_price_drop") and price_change < 0:
            price_alerts.append({
                "player": player.get("web_name"),
                "alert": f"Price dropped by £{abs(price_change)}m since added",
            })
        
        if entry.get("alert_on_price_rise") and price_change > 0:
            price_alerts.append({
                "player": player.get("web_name"),
                "alert": f"Price rose by £{price_change}m since added",
            })
        
        # Get upcoming fixtures
        upcoming = get_upcoming_fixtures_for_team(player.get("team"), 3)
        
        enriched_players.append({
            **entry,
            "status": player.get("status", "a"),
            "current_price": current_price,
            "price_change": price_change,
            "price_change_display": f"+£{price_change}m" if price_change > 0 else f"£{price_change}m" if price_change < 0 else "No change",
            "form": float(player.get("form", 0) or 0),
            "total_points": player.get("total_points", 0),
            "points_per_game": float(player.get("points_per_game", 0) or 0),
            "selected_by_percent": float(player.get("selected_by_percent", 0) or 0),
            "news": player.get("news", ""),
            "upcoming_fixtures": upcoming,
            "transfers_in_event": player.get("transfers_in_event", 0),
            "transfers_out_event": player.get("transfers_out_event", 0),
        })
    
    # Sort by price change (biggest movers first)
    enriched_players.sort(key=lambda x: abs(x.get("price_change", 0) or 0), reverse=True)
    
    return {
        "watchlist": enriched_players,
        "count": len(enriched_players),
        "price_alerts": price_alerts,
        "summary": {
            "total_players": len(enriched_players),
            "price_risers": sum(1 for p in enriched_players if (p.get("price_change") or 0) > 0),
            "price_fallers": sum(1 for p in enriched_players if (p.get("price_change") or 0) < 0),
            "flagged_players": sum(1 for p in enriched_players if p.get("news")),
        },
        "_meta": {
            "fetched_at": datetime.now().isoformat(),
            "source": "watchlist",
        }
    }


def update_watchlist_notes(player_name: str, notes: str) -> Dict[str, Any]:
    """
    Update notes for a player on the watchlist.
    
    Args:
        player_name: Player name
        notes: New notes
        
    Returns:
        Confirmation
    """
    load_core_game_data()
    
    player = get_player_by_name(player_name)
    if not player:
        return {"error": f"Player '{player_name}' not found"}
    
    player_id = player.get("id")
    watchlist = _load_watchlist()
    
    found = False
    for p in watchlist["players"]:
        if p.get("player_id") == player_id:
            p["notes"] = notes
            p["notes_updated_at"] = datetime.now().isoformat()
            found = True
            break
    
    if not found:
        return {"error": f"{player.get('web_name')} is not on your watchlist"}
    
    _save_watchlist(watchlist)
    
    return {
        "success": True,
        "message": f"Updated notes for {player.get('web_name')}",
        "_meta": {
            "action": "update_notes",
            "timestamp": datetime.now().isoformat(),
        }
    }


def clear_watchlist() -> Dict[str, Any]:
    """
    Clear all players from the watchlist.
    
    Returns:
        Confirmation
    """
    watchlist = _load_watchlist()
    count = len(watchlist.get("players", []))
    
    watchlist["players"] = []
    _save_watchlist(watchlist)
    
    return {
        "success": True,
        "message": f"Cleared {count} players from watchlist",
        "_meta": {
            "action": "clear",
            "timestamp": datetime.now().isoformat(),
        }
    }
