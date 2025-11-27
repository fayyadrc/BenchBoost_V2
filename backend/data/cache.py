"""
FPL Data Cache with TTL-based Expiration

Enhanced caching system for optimal LLM context access:
- TTL-based cache entries with automatic expiration
- Configurable refresh intervals per data type
- Cache statistics and monitoring
- Smart invalidation on data updates
"""

from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import requests
from .api_client import bootstrap_static, fixtures, DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


# ============================================================================
# TTL-BASED CACHE IMPLEMENTATION
# ============================================================================

@dataclass
class CacheEntry:
    """Cache entry with TTL-based expiration."""
    data: Any
    created_at: datetime
    ttl_seconds: int
    
    @property
    def expires_at(self) -> datetime:
        """Calculate expiration time."""
        return self.created_at + timedelta(seconds=self.ttl_seconds)
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.now() > self.expires_at
    
    def time_until_expiry(self) -> timedelta:
        """Get time remaining until expiry."""
        return self.expires_at - datetime.now()


# Cache TTL configuration (in seconds)
CACHE_TTL = {
    "players": 3600,        # 1 hour - player data changes frequently
    "teams": 86400,         # 24 hours - team data is mostly static
    "gameweeks": 3600,      # 1 hour - gameweek status changes
    "fixtures": 21600,      # 6 hours - fixtures update occasionally
    "bootstrap_static": 3600,  # 1 hour - main data source
    "current_gameweek": 3600,  # 1 hour - current GW changes weekly
}

# Module-level cache storage
_cache: Dict[str, CacheEntry] = {}

# Cache statistics
_cache_stats = {
    "hits": 0,
    "misses": 0,
    "expirations": 0,
    "invalidations": 0,
}


# ============================================================================
# CORE CACHE OPERATIONS
# ============================================================================

def _get_from_cache(key: str) -> Optional[Any]:
    """
    Get data from cache if valid, None if expired or missing.
    
    Args:
        key: Cache key
        
    Returns:
        Cached data or None
    """
    if key not in _cache:
        _cache_stats["misses"] += 1
        return None
    
    entry = _cache[key]
    
    if entry.is_expired():
        logger.debug(f"Cache expired for key: {key}")
        _cache_stats["expirations"] += 1
        del _cache[key]
        return None
    
    _cache_stats["hits"] += 1
    logger.debug(f"Cache hit for key: {key} (expires in {entry.time_until_expiry()})")
    return entry.data


def _set_in_cache(key: str, data: Any, ttl_seconds: Optional[int] = None) -> None:
    """
    Store data in cache with TTL.
    
    Args:
        key: Cache key
        data: Data to cache
        ttl_seconds: Time to live in seconds (uses default if None)
    """
    if ttl_seconds is None:
        ttl_seconds = CACHE_TTL.get(key, 3600)  # Default 1 hour
    
    _cache[key] = CacheEntry(
        data=data,
        created_at=datetime.now(),
        ttl_seconds=ttl_seconds
    )
    logger.debug(f"Cached key: {key} (TTL: {ttl_seconds}s)")


def invalidate_cache(key: Optional[str] = None) -> None:
    """
    Invalidate cache entry or entire cache.
    
    Args:
        key: Specific key to invalidate, or None to clear all
    """
    global _cache
    
    if key is None:
        logger.info("Clearing entire cache")
        _cache.clear()
        _cache_stats["invalidations"] += len(_cache)
    elif key in _cache:
        logger.info(f"Invalidating cache key: {key}")
        del _cache[key]
        _cache_stats["invalidations"] += 1


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache performance statistics.
    
    Returns:
        Dict with cache statistics
    """
    total_requests = _cache_stats["hits"] + _cache_stats["misses"]
    hit_rate = (_cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
    
    return {
        **_cache_stats,
        "total_requests": total_requests,
        "hit_rate_percent": round(hit_rate, 2),
        "cache_size": len(_cache),
        "cached_keys": list(_cache.keys()),
    }


# ============================================================================
# LEGACY CORE DATA STRUCTURE (for backward compatibility)
# ============================================================================

# Core game data dictionaries - organized for easy access
core_data: Dict[str, Any] = {
    "players": {},  # player_id -> player details
    "teams": {},  # team_id -> team details
    "gameweeks": {},  # gameweek_id -> gameweek details
    "fixtures": {},  # fixture_id -> fixture details
    "players_by_name": {},  # player_name -> player details (for quick lookup)
    "teams_by_name": {},  # team_name -> team details
}


# ============================================================================
# DATA LOADING WITH CACHING
# ============================================================================

def load_core_game_data(
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Load all core FPL game data with caching.
    
    This fetches and organizes:
    - All players (with stats, filtering out transferred players)
    - All teams
    - All gameweeks
    - All fixtures
    
    Data is cached with TTL and stored in module-level `core_data` dict.
    
    Args:
        session: Optional requests session
        timeout: Request timeout
        force_refresh: Force cache refresh even if valid
        
    Returns:
        Dict with the organized core data
    """
    global core_data
    
    # Check cache first (unless force refresh)
    if not force_refresh:
        cached = _get_from_cache("core_game_data")
        if cached is not None:
            core_data = cached
            return core_data
    
    logger.info("Loading core game data from API...")
    
    # Fetch bootstrap-static (main data source)
    bs = bootstrap_static(session=session, timeout=timeout)
    
    # Organize players by ID and name
    core_data["players"] = {}
    core_data["players_by_name"] = {}
    
    for player in bs.get("elements", []):
        # Skip players who transferred out of Premier League
        if player.get("status") == "u":
            continue
        
        player_id = player.get("id")
        web_name = player.get("web_name", "")
        full_name = f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
        
        core_data["players"][player_id] = player
        if web_name:
            core_data["players_by_name"][web_name.lower()] = player
        if full_name:
            # Also map full name to enable queries like "Erling Haaland"
            core_data["players_by_name"][full_name.lower()] = player
    
    # Organize teams by ID and name
    core_data["teams"] = {}
    core_data["teams_by_name"] = {}
    
    for team in bs.get("teams", []):
        team_id = team.get("id")
        team_name = team.get("name", "")
        team_short_name = team.get("short_name", "")
        
        core_data["teams"][team_id] = team
        if team_name:
            core_data["teams_by_name"][team_name.lower()] = team
        if team_short_name:
            core_data["teams_by_name"][team_short_name.lower()] = team
    
    # Organize gameweeks by ID
    core_data["gameweeks"] = {}
    
    for event in bs.get("events", []):
        event_id = event.get("id")
        core_data["gameweeks"][event_id] = event
    
    # Fetch and organize all fixtures
    all_fixtures = fixtures(session=session, timeout=timeout)
    core_data["fixtures"] = {}
    
    for fixture in all_fixtures:
        fixture_id = fixture.get("id")
        core_data["fixtures"][fixture_id] = fixture
    
    # Store full bootstrap data for reference
    core_data["bootstrap_static"] = bs
    core_data["game_settings"] = bs.get("game_settings", {})
    
    # Cache the loaded data
    _set_in_cache("core_game_data", core_data, CACHE_TTL["bootstrap_static"])
    
    logger.info(f"Loaded {len(core_data['players'])} players, "
                f"{len(core_data['teams'])} teams, "
                f"{len(core_data['gameweeks'])} gameweeks, "
                f"{len(core_data['fixtures'])} fixtures")
    
    return core_data


# ============================================================================
# LOOKUP FUNCTIONS
# ============================================================================

def get_player_by_id(player_id: int) -> Optional[Dict[str, Any]]:
    """Get player details by ID from core_data cache."""
    return core_data.get("players", {}).get(player_id)


def get_player_by_name(player_name: str) -> Optional[Dict[str, Any]]:
    """Get player details by name (case-insensitive) from core_data cache."""
    return core_data.get("players_by_name", {}).get(player_name.lower())


def get_team_by_id(team_id: int) -> Optional[Dict[str, Any]]:
    """Get team details by ID from core_data cache."""
    return core_data.get("teams", {}).get(team_id)


def get_team_by_name(team_name: str) -> Optional[Dict[str, Any]]:
    """Get team details by name (case-insensitive) from core_data cache."""
    return core_data.get("teams_by_name", {}).get(team_name.lower())


def get_gameweek_by_id(gameweek_id: int) -> Optional[Dict[str, Any]]:
    """Get gameweek details by ID from core_data cache."""
    return core_data.get("gameweeks", {}).get(gameweek_id)


def get_current_gameweek() -> Optional[Dict[str, Any]]:
    """Get the current active gameweek from core_data cache."""
    for gw in core_data.get("gameweeks", {}).values():
        if gw.get("is_current"):
            return gw
    return None


def get_fixture_by_id(fixture_id: int) -> Optional[Dict[str, Any]]:
    """Get fixture details by ID from core_data cache."""
    return core_data.get("fixtures", {}).get(fixture_id)


def get_upcoming_fixtures_for_team(team_id: int, num_fixtures: int = 3) -> list:
    """
    Get upcoming fixtures for a specific team.
    
    Args:
        team_id: Team ID
        num_fixtures: Number of upcoming fixtures to return
        
    Returns:
        List of fixture dictionaries
    """
    current_gw = get_current_gameweek()
    if not current_gw:
        return []
        
    current_event = current_gw.get("id", 1)
    
    upcoming = []
    all_fixtures = core_data.get("fixtures", {}).values()
    
    # Sort fixtures by event
    sorted_fixtures = sorted(
        [f for f in all_fixtures if f.get("event") is not None], 
        key=lambda x: x.get("event")
    )
    
    for fixture in sorted_fixtures:
        if fixture.get("event") < current_event:
            continue
            
        if fixture.get("team_h") == team_id or fixture.get("team_a") == team_id:
            is_home = fixture.get("team_h") == team_id
            opponent_id = fixture.get("team_a") if is_home else fixture.get("team_h")
            opponent = get_team_by_id(opponent_id)
            
            upcoming.append({
                "event": fixture.get("event"),
                "is_home": is_home,
                "opponent_id": opponent_id,
                "opponent_name": opponent.get("name") if opponent else "Unknown",
                "opponent_short": opponent.get("short_name") if opponent else "UNK",
                "difficulty": fixture.get("team_h_difficulty") if is_home else fixture.get("team_a_difficulty")
            })
            
            if len(upcoming) >= num_fixtures:
                break
                
    return upcoming


def get_cached_player_news(force_refresh: bool = False) -> list:
    """
    Get player news (injuries/price changes) with caching.
    
    Args:
        force_refresh: Force a fresh scrape
        
    Returns:
        List of news items
    """
    cache_key = "player_news_alerts"
    
    # Check cache first
    if not force_refresh:
        cached = _get_from_cache(cache_key)
        if cached is not None:
            return cached
            
    # If not in cache or forced refresh, fetch fresh data
    try:
        from .player_injury_status import scrape_fpl_alerts
        logger.info("Scraping fresh player news...")
        news = scrape_fpl_alerts()
        
        # Cache for 15 minutes (900 seconds)
        _set_in_cache(cache_key, news, ttl_seconds=10800)
        return news
    except Exception as e:
        logger.error(f"Failed to scrape player news: {e}")
        return []