"""
Shared constants for FPL data processing.
Centralizes numbers and mappings to avoid duplication
"""

# =============================================================================
# POSITION MAPPINGS
# =============================================================================

# Position ID to name mapping (consistent abbreviations)
POSITION_ID_TO_NAME = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}
POSITION_NAME_TO_ID = {"GKP": 1, "GK": 1, "DEF": 2, "MID": 3, "FWD": 4, "FORWARD": 4, "STRIKER": 4}

# Position ID to full name
POSITION_ID_TO_FULL_NAME = {
    1: "Goalkeeper",
    2: "Defender", 
    3: "Midfielder",
    4: "Forward"
}

# =============================================================================
# API CONFIGURATION
# =============================================================================

FPL_BASE_URL = "https://fantasy.premierleague.com/api"
DEFAULT_TIMEOUT = 10.0

# =============================================================================
# CACHE TTLS (in seconds)
# =============================================================================

CACHE_TTL = {
    "bootstrap_static": 3600,      # 1 hour
    "current_gameweek": 3600,      # 1 hour  
    "fixtures": 3600,              # 1 hour
    "player_stats": 1800,          # 30 minutes
    "live_data": 60,               # 1 minute
    "manager_data": 300,           # 5 minutes
    "element_summary": 1800,       # 30 minutes - player history
    "transfers": 300,              # 5 minutes - transfer data
    "league_standings": 600,       # 10 minutes
}

# =============================================================================
# SCORING SYSTEM
# =============================================================================

SCORING = {
    "goals": {
        1: 6,   # GKP
        2: 6,   # DEF
        3: 5,   # MID
        4: 4,   # FWD
    },
    "assists": 3,
    "clean_sheet": {
        1: 4,   # GKP
        2: 4,   # DEF
        3: 1,   # MID
        4: 0,   # FWD
    },
    "appearance_60_plus": 2,
    "appearance_under_60": 1,
    "goals_conceded_2": -1,  # Per 2 goals conceded (GKP/DEF)
    "penalty_save": 5,
    "penalty_miss": -2,
    "saves_3": 1,           # Per 3 saves (GKP)
    "yellow_card": -1,
    "red_card": -3,
    "own_goal": -2,
    "bonus_max": 3,
}

# =============================================================================
# GAME RULES
# =============================================================================

GAME_RULES = {
    "squad_size": 15,
    "starting_xi": 11,
    "bench_size": 4,
    "max_players_per_team": 3,
    "starting_budget": 100.0,
    "free_transfers_per_week": 1,
    "max_banked_transfers": 2,
    "transfer_cost": 4,         # Points deducted per extra transfer
    "captain_multiplier": 2,
    "triple_captain_multiplier": 3,
}

# =============================================================================
# FIXTURE DIFFICULTY
# =============================================================================

FIXTURE_DIFFICULTY = {
    1: "Very Easy",
    2: "Easy", 
    3: "Medium",
    4: "Hard",
    5: "Very Hard",
}

# Thresholds for fixture analysis
FIXTURE_THRESHOLDS = {
    "easy_max": 2.5,        # Average FDR below this = easy run
    "medium_max": 3.5,      # Average FDR below this = medium run
    # Above 3.5 = hard run
}

# =============================================================================
# OWNERSHIP TIERS
# =============================================================================

OWNERSHIP_TIERS = {
    "template": 40.0,       # >= 40% = template/essential
    "popular": 20.0,        # >= 20% = popular pick
    "differential": 5.0,    # >= 5% = good differential
    # Below 5% = punt
}

# =============================================================================
# FORM THRESHOLDS
# =============================================================================

FORM_THRESHOLDS = {
    "excellent": 7.0,       # >= 7.0 = excellent form
    "good": 5.0,            # >= 5.0 = good form
    "average": 3.0,         # >= 3.0 = average form
    # Below 3.0 = poor form
}

# =============================================================================
# VALUE THRESHOLDS
# =============================================================================

VALUE_THRESHOLDS = {
    "premium_min": 10.0,    # >= £10.0m = premium
    "mid_price_min": 6.5,   # >= £6.5m = mid-price
    "budget_min": 5.0,      # >= £5.0m = budget
    # Below £5.0m = enabler/fodder
}

# =============================================================================
# TRANSFER TREND THRESHOLDS
# =============================================================================

TRANSFER_THRESHOLDS = {
    "very_hot": 50000,      # >= 50k net = very hot
    "rising": 20000,        # >= 20k net = rising
    "falling": -20000,      # <= -20k net = dropping
    "falling_fast": -50000, # <= -50k net = falling fast
}

# =============================================================================
# METRICS
# =============================================================================

# Valid metrics for sorting/filtering
VALID_PLAYER_METRICS = [
    "total_points",
    "points_per_game",
    "form",
    "goals_scored",
    "assists",
    "clean_sheets",
    "bonus",
    "bps",
    "ict_index",
    "influence",
    "creativity",
    "threat",
    "now_cost",
    "selected_by_percent",
    "minutes",
    "expected_goals",
    "expected_assists",
    "expected_goal_involvements",
    "transfers_in_event",
    "transfers_out_event",
    "points_per_million",
    "points_per_90",
]

# Human-readable metric names
METRIC_DISPLAY_NAMES = {
    "total_points": "Total Points",
    "points_per_game": "Points Per Game",
    "form": "Form",
    "goals_scored": "Goals",
    "assists": "Assists",
    "clean_sheets": "Clean Sheets",
    "bonus": "Bonus Points",
    "bps": "BPS",
    "ict_index": "ICT Index",
    "influence": "Influence",
    "creativity": "Creativity",
    "threat": "Threat",
    "now_cost": "Price",
    "selected_by_percent": "Ownership %",
    "minutes": "Minutes",
    "expected_goals": "xG",
    "expected_assists": "xA",
    "expected_goal_involvements": "xGI",
    "transfers_in_event": "Transfers In",
    "transfers_out_event": "Transfers Out",
    "points_per_million": "Points Per Million",
    "points_per_90": "Points Per 90",
}

# =============================================================================
# CHIP TYPES
# =============================================================================

CHIP_NAMES = {
    "wildcard": "Wildcard",
    "freehit": "Free Hit",
    "bboost": "Bench Boost",
    "3xc": "Triple Captain",
}

# =============================================================================
# AVAILABILITY STATUS
# =============================================================================

AVAILABILITY_STATUS = {
    "a": "Available",
    "d": "Doubtful (25-75%)",
    "i": "Injured",
    "s": "Suspended",
    "n": "Not Available",
    "u": "Unavailable (Transferred Out)",
}
