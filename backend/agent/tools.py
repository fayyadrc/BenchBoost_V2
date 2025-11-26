"""Tool definitions exposed to the LLM.

All tools use the unified `langchain_core.tools.tool` decorator for consistency
with LangChain 1.x + LangGraph. Each function wraps underlying data-layer
helpers and returns raw dicts/objects suitable for the agent to format.
"""

from typing import Optional, Any, Dict, List
from ..data import api_client, cache, livefpl_scrape, stats
from . import context_builder
from langchain_core.tools import tool


# -----------------------------
# PLAYER + STATS TOOLS
# -----------------------------

@tool
def get_all_players_with_stats(session: Optional[Any] = None, timeout: Optional[int] = None) -> List[Dict]:
    """Get all players with calculated statistics (PPM, points per 90, etc.)."""
    return stats.get_all_players_with_stats(session=session, timeout=timeout)


@tool
def get_player_stats(player_name: str, session: Optional[Any] = None, timeout: Optional[int] = None) -> Dict:
    """Get stats for a specific player by name."""
    return stats.get_player_stats(player_name, session=session, timeout=timeout)


@tool
def get_best_players(
    position: Optional[str] = None,
    sort_by: str = "points_per_million_per_90",
    count: int = 5,
    session: Optional[Any] = None,
    timeout: Optional[int] = None,
) -> List[Dict]:
    """Return the best players by position and sort criteria."""
    return stats.get_best_players(
        position=position,
        sort_by=sort_by,
        count=count,
        session=session,
        timeout=timeout
    )


# -----------------------------
# RULES + LOOKUP TOOLS
# -----------------------------

@tool
def get_fpl_rules() -> Dict:
    """Return the full FPL rules knowledge base + formatted string."""
    return stats.get_fpl_rules()


@tool
def get_player_info(player_name: str, include_stats: bool = True, formatted: bool = False) -> Dict | str:
    """
    Get comprehensive player information with smart caching.
    
    This tool automatically uses cache → MongoDB → API in that order.
    Use this instead of get_player_by_name for better performance.
    
    Args:
        player_name: Player's web name or full name
        include_stats: Include calculated statistics (PPM, points per 90, etc.)
        formatted: Return LLM-optimized formatted string instead of raw dict
        
    Returns:
        Player data dict or formatted string
    """
    # Try cache first (fast path)
    player = cache.get_player_by_name(player_name)
    
    if not player:
        # Fallback: load core data if not already loaded
        cache.load_core_game_data()
        player = cache.get_player_by_name(player_name)
    
    if not player:
        return {"error": f"Player '{player_name}' not found"}
    
    # Enrich with calculated stats if requested
    if include_stats:
        try:
            player_stats = stats.get_player_stats(player_name)
            if player_stats and "error" not in player_stats:
                player["calculated_stats"] = player_stats
        except Exception:
            pass  # Stats are optional
    
    # Return formatted context if requested
    if formatted:
        return context_builder.build_player_context([player_name])
    
    return player


@tool
def get_player_by_name(player_name: str) -> Dict:
    """Fast lookup for one specific player. Consider using get_player_info for more features."""
    return cache.get_player_by_name(player_name)


@tool
def get_current_gameweek() -> Dict:
    """Get the current gameweek information."""
    return cache.get_current_gameweek()


@tool
def get_gameweek_summary(gameweek_id: Optional[int] = None) -> str:
    """
    Get a formatted summary of gameweek information.
    
    Args:
        gameweek_id: Specific gameweek ID, or None for current gameweek
        
    Returns:
        Formatted gameweek summary with deadline, status, and chip usage
    """
    return context_builder.build_gameweek_summary(gameweek_id)


@tool
def get_team_by_name(team_name: str) -> Dict:
    """Get information about a specific Premier League team."""
    return cache.get_team_by_name(team_name)


@tool
def get_team_summary(team_name: str) -> str:
    """
    Get a formatted summary of team information including strength ratings.
    
    Args:
        team_name: Team name (full or short name)
        
    Returns:
        Formatted team summary
    """
    return context_builder.build_team_summary(team_name)


@tool
def get_fixture_difficulty(team_name: str, num_fixtures: int = 5) -> str:
    """
    Analyze upcoming fixture difficulty for a team.
    
    Args:
        team_name: Team name
        num_fixtures: Number of upcoming fixtures to analyze (default 5)
        
    Returns:
        Formatted fixture difficulty narrative
    """
    return context_builder.build_fixture_difficulty_narrative(team_name, num_fixtures)


# -----------------------------
# DATA LOADING TOOLS
# -----------------------------

@tool
def load_core_game_data(session: Optional[Any] = None, timeout: Optional[int] = None, force_refresh: bool = False) -> Dict:
    """
    Load all core FPL data with caching (players, teams, gameweeks, fixtures).
    
    Args:
        session: Optional requests session
        timeout: Request timeout
        force_refresh: Force cache refresh even if valid
        
    Returns:
        Dict with all core game data
    """
    return cache.load_core_game_data(session=session, timeout=timeout, force_refresh=force_refresh)


# -----------------------------
# LIVEFPL SCRAPER
# -----------------------------

@tool
def scrape_livefpl_data(entry_id: int, headless: bool = True, timeout: int = 180000) -> Dict:
    """Scrape FPL data from plan.livefpl.net for a given entry ID."""
    return livefpl_scrape.scrape_livefpl_data(entry_id, headless=headless, timeout=timeout)


# -----------------------------
# FPL API CLIENT
# -----------------------------

@tool
def bootstrap_static(session: Optional[Any] = None, timeout: Optional[int] = None) -> Dict:
    """Get bootstrap-static data (events, elements, teams, etc.)."""
    return api_client.bootstrap_static(session=session, timeout=timeout)


@tool
def event_live(event_id: int, session: Optional[Any] = None, timeout: Optional[int] = None) -> Dict:
    """Get live event data for a specific gameweek."""
    return api_client.event_live(event_id, session=session, timeout=timeout)


# -----------------------------
# MANAGER-LEVEL DATA
# -----------------------------

@tool
def get_manager_info(entry_id: int, session: Optional[Any] = None, timeout: Optional[int] = None) -> Dict:
    """Get a manager's profile (team name, OR, team value)."""
    return api_client.entry_summary(entry_id, session=session, timeout=timeout)


@tool
def get_manager_squad(entry_id: int, event_id: Optional[int] = None) -> Dict:
    """
    Get a manager's current squad with player details for captain/transfer advice.
    
    IMPORTANT: Use this tool FIRST when the user asks personal questions like:
    - "Who should I captain?"
    - "Who should I bench?"
    - "Transfer suggestions for my team"
    - "Rate my team"
    - Any question about "my team" or "my players"
    
    Args:
        entry_id: The manager's FPL entry ID
        event_id: Optional gameweek number (defaults to current GW)
    
    Returns:
        Dict with starting_xi, bench, and player details (name, team, position, form, points, fixtures)
    """
    from ..data.manager_data import get_manager_squad_data
    return get_manager_squad_data(entry_id, event_id)


@tool
def get_live_gameweek_data(entry_id: int, session: Optional[Any] = None, timeout: Optional[int] = None) -> Dict:
    """Get a manager's live GW performance."""
    return livefpl_scrape.scrape_livefpl_data(entry_id)


# -----------------------------
# RAG / KNOWLEDGE BASE TOOLS
# -----------------------------

@tool
def search_knowledge_base(query: str) -> List[str]:
    """
    Search the FPL knowledge base for qualitative info (rules, news, injuries).
    Use this for questions like "Is Haaland injured?", "How do bonus points work?", 
    or "What is the latest news on Isak?".
    """
    import os
    from pymongo import MongoClient
    from langchain_mongodb import MongoDBAtlasVectorSearch
    from langchain_huggingface import HuggingFaceEmbeddings
    from dotenv import load_dotenv

    load_dotenv()

    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME")
    COLLECTION_NAME = "fpl_knowledge_base"
    ATLAS_VECTOR_SEARCH_INDEX_NAME = "default"

    if not MONGO_URI:
        return ["Error: MONGO_URI not set."]

    try:
        # Initialize Embeddings (runs locally)
        embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # Connect to Mongo
        client = MongoClient(MONGO_URI)
        collection = client[DB_NAME][COLLECTION_NAME]
        
        # Initialize Vector Store
        vectorstore = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embedding_function,
            index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME
        )
        
        # Search for top 4 relevant documents
        results = vectorstore.similarity_search(query, k=4)
        return [doc.page_content for doc in results]
    except Exception as e:
        return [f"Error searching knowledge base: {str(e)}"]


# -----------------------------
# CONTEXT BUILDING TOOLS
# -----------------------------

@tool
def compare_players(player_names: List[str], sort_by: str = "total_points") -> str:
    """
    Compare multiple players side-by-side.
    
    Args:
        player_names: List of player names to compare
        sort_by: Metric to sort by (total_points, form, now_cost, etc.)
        
    Returns:
        Formatted comparison table
    """
    return context_builder.build_player_comparison(player_names, sort_by)


@tool
def get_top_players(position: Optional[str] = None, metric: str = "total_points", count: int = 10) -> str:
    """
    Get top players by a specific metric.
    
    Args:
        position: Filter by position (GK, DEF, MID, FWD) or None for all
        metric: Metric to sort by (total_points, form, selected_by_percent, etc.)
        count: Number of players to return (default 10)
        
    Returns:
        Formatted list of top players
    """
    return context_builder.build_top_players_summary(position, metric, count)


# -----------------------------
# CACHE MANAGEMENT TOOLS
# -----------------------------

@tool
def get_cache_statistics() -> Dict:
    """
    Get cache performance statistics.
    
    Returns:
        Dict with cache hits, misses, hit rate, and cached keys
    """
    return cache.get_cache_stats()


@tool
def refresh_cache() -> str:
    """
    Force refresh the cache by invalidating and reloading core data.
    
    Returns:
        Status message
    """
    cache.invalidate_cache()
    cache.load_core_game_data(force_refresh=True)
    return "Cache refreshed successfully"

# -----------------------------
# EXPORT TOOL LIST
# -----------------------------

all_tools = [
    # High-level composite tools (use these first)
    get_player_info,
    compare_players,
    get_top_players,
    get_gameweek_summary,
    get_team_summary,
    get_fixture_difficulty,
    
    # Player & stats tools
    get_all_players_with_stats,
    get_player_stats,
    get_best_players,
    
    # Rules & lookup tools
    get_fpl_rules,
    get_player_by_name,
    get_current_gameweek,
    get_team_by_name,
    
    # Data loading
    load_core_game_data,
    
    # Live data & scraping
    scrape_livefpl_data,
    get_manager_info,
    get_manager_squad,
    get_live_gameweek_data,
    
    # API tools (use sparingly)
    bootstrap_static,
    event_live,
    
    # Cache management
    get_cache_statistics,
    refresh_cache,
]
