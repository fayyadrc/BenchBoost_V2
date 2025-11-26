"""
Shared constants for FPL data processing.
Centralizes magic numbers and mappings to avoid duplication.
"""

# Position ID to name mapping (consistent abbreviations)
POSITION_ID_TO_NAME = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}
POSITION_NAME_TO_ID = {"GKP": 1, "GK": 1, "DEF": 2, "MID": 3, "FWD": 4}

# Position ID to full name
POSITION_ID_TO_FULL_NAME = {
    1: "Goalkeeper",
    2: "Defender", 
    3: "Midfielder",
    4: "Forward"
}

# API Configuration
FPL_BASE_URL = "https://fantasy.premierleague.com/api"
DEFAULT_TIMEOUT = 10.0

# Cache TTLs (in seconds)
CACHE_TTL = {
    "bootstrap_static": 3600,      # 1 hour
    "current_gameweek": 3600,      # 1 hour  
    "fixtures": 3600,              # 1 hour
    "player_stats": 1800,          # 30 minutes
    "live_data": 60,               # 1 minute
    "manager_data": 300,           # 5 minutes
}
