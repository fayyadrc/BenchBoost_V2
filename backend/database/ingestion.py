import sys
import os
import logging
import time
from datetime import datetime, timezone

# --- Path Setup ---
# Add the project root to sys.path to allow imports from backend.*
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(project_root)

# --- Imports ---
from backend.data.api_client import bootstrap_static, fixtures
from backend.data.player_injury_status import get_all_players
from backend.database.db import get_db
from pymongo import ASCENDING, DESCENDING

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def create_indexes(db):
    """
    Defines and creates the schema indexes for efficient querying.
    """
    logger.info("⚙️ Creating indexes...")

    # 1. Players Collection
    # Queries: By ID, By Name (text search), By Team, By Price/Stats
    db.players.create_index([("id", ASCENDING)], unique=True)
    db.players.create_index([("web_name", ASCENDING)])
    db.players.create_index([("second_name", ASCENDING)])
    db.players.create_index([("team", ASCENDING)])
    db.players.create_index([("element_type", ASCENDING)])  # Position
    # Compound index for sorting value
    db.players.create_index([("now_cost", ASCENDING), ("total_points", DESCENDING)])

    # 2. Teams Collection
    db.teams.create_index([("id", ASCENDING)], unique=True)
    db.teams.create_index([("name", ASCENDING)])
    db.teams.create_index([("short_name", ASCENDING)])

    # 3. Gameweeks (Events) Collection
    db.gameweeks.create_index([("id", ASCENDING)], unique=True)
    db.gameweeks.create_index([("is_current", ASCENDING)])
    db.gameweeks.create_index([("is_next", ASCENDING)])

    # 4. Fixtures Collection
    db.fixtures.create_index([("id", ASCENDING)], unique=True)
    db.fixtures.create_index([("event", ASCENDING)])  # Filter by Gameweek
    db.fixtures.create_index([("team_h", ASCENDING)]) # Filter by Home Team
    db.fixtures.create_index([("team_a", ASCENDING)]) # Filter by Away Team
    db.fixtures.create_index([("kickoff_time", ASCENDING)])

    logger.info("✅ Indexes created successfully.")

def update_static_data():
    """
    Main ingestion logic:
    1. Fetches fresh data from FPL API.
    2. Transforms/Cleans data if necessary.
    3. Replaces existing collections in MongoDB.
    """
    start_time = time.time()
    logger.info("🚀 Starting FPL Static Data Ingestion...")

    try:
        db = get_db()
        
        # --- STEP 1: Fetch Data ---
        logger.info("📡 Fetching bootstrap-static data from FPL API...")
        bootstrap = bootstrap_static()
        if not isinstance(bootstrap, dict):
            raise ValueError("bootstrap_static did not return a dict")
        
        logger.info("📡 Fetching all fixtures from FPL API...")
        all_fixtures = fixtures()
        if not isinstance(all_fixtures, list):
            raise ValueError("fixtures did not return a list")

        # --- STEP 2: Process & Insert Teams ---
        teams = bootstrap.get("teams", [])
        if teams:
            logger.info(f"💾 Upserting {len(teams)} teams...")
            # Strategy: Drop and Insert ensures clean state for static data
            db.teams.drop()
            db.teams.insert_many(teams)
        
        # --- STEP 3: Process & Insert Players (Elements) ---
        # raw_players = bootstrap.get("elements", [])
        logger.info("📡 Fetching player profiles from player_data.py...")
        raw_players = get_all_players()
        # Filter: Optional - remove players who have left the league (status = 'u')
        # keeping 'i' (injured) and 's' (suspended) as they are still entities
        active_players = [p for p in raw_players if p.get("status") != "u"]
        
        if active_players:
            logger.info(f"💾 Upserting {len(active_players)} players (filtered from {len(raw_players)} total)...")
            db.players.drop()
            # Add a timestamp to track when this data was last updated
            for p in active_players:
                p["_last_updated"] = datetime.now(timezone.utc)
            db.players.insert_many(active_players)

        # --- STEP 4: Process & Insert Gameweeks (Events) ---
        events = bootstrap.get("events", [])
        if events:
            logger.info(f"💾 Upserting {len(events)} gameweeks...")
            db.gameweeks.drop()
            db.gameweeks.insert_many(events)

        # --- STEP 5: Process & Insert Fixtures ---
        if all_fixtures:
            logger.info(f"💾 Upserting {len(all_fixtures)} fixtures...")
            db.fixtures.drop()
            db.fixtures.insert_many(all_fixtures)

        # --- STEP 6: Apply Schema/Indexes ---
        create_indexes(db)
        
        # --- STEP 7: Invalidate Cache ---
        # Ensure cache is cleared after database update
        try:
            from backend.data import cache
            cache.invalidate_cache()
            logger.info("✅ Cache invalidated after database update")
        except Exception as cache_error:
            logger.warning(f"⚠️  Failed to invalidate cache: {cache_error}")

        elapsed = time.time() - start_time
        logger.info(f"✅ Data ingestion complete in {elapsed:.2f} seconds.")

    except Exception as e:
        logger.error(f"❌ Data ingestion failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    update_static_data()
