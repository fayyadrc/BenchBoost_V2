import sys
import os
import logging
import time
from datetime import datetime, timezone

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(project_root)

# --- Imports ---
from backend.data.core.api_client import bootstrap_static, fixtures
from backend.database.db import get_db
from backend.data.scrapers.videoprinter_data import fetch_updates
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

    # 1. Price Changes Collection
    db.price_changes.create_index([
        ("player", ASCENDING),
        ("timestamp", DESCENDING)
    ], unique=True)
    db.price_changes.create_index([("team", ASCENDING)])
    db.price_changes.create_index([("change_type", ASCENDING)])  # "rise" or "fall"
    db.price_changes.create_index([("timestamp", DESCENDING)])

    # 2. Player Status/Injuries Collection
    db.player_status.create_index([
        ("player", ASCENDING),
        ("timestamp", DESCENDING)
    ])
    db.player_status.create_index([("team", ASCENDING)])
    db.player_status.create_index([("status", "text")])  # Full-text search on injury description

    # 3. Match Events Collection (goals, cards, saves, etc.)
    db.match_events.create_index([
        ("home_team", ASCENDING),
        ("event_type", ASCENDING),
        ("timestamp", DESCENDING)
    ])
    db.match_events.create_index([("player", ASCENDING)])
    db.match_events.create_index([("event_type", ASCENDING)])  # "goal", "yellow_card", etc.
    db.match_events.create_index([("timestamp", DESCENDING)])

    # 4. Bonus Points Collection
    db.bonus_points.create_index([
        ("home_team", ASCENDING),
        ("timestamp", DESCENDING)
    ])
    db.bonus_points.create_index([("timestamp", DESCENDING)])

    # 5. Match Updates Collection (KO, HT, FT)
    db.match_updates.create_index([
        ("home_team", ASCENDING),
        ("away_team", ASCENDING),
        ("timestamp", DESCENDING)
    ])
    db.match_updates.create_index([("timestamp", DESCENDING)])

    # 6. Team News Collection
    db.team_news.create_index([("timestamp", DESCENDING)])
    db.team_news.create_index([("content", "text")])  # Full-text search

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
        raw_players = bootstrap.get("elements", [])
        logger.info(f"📡 Fetched {len(raw_players)} player profiles from bootstrap-static...")
        # raw_players = get_all_players()
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

        # --- STEP 6: Process & Insert Videoprinter Updates ---
        update_videoprinter_data()

        # --- STEP 7: Apply Schema/Indexes ---
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

def update_videoprinter_data():
    """
    Fetch and upsert Videoprinter data (Price Changes, Status, Matches).
    """
    logger.info("📡 Fetching Videoprinter updates...")
    try:
        db = get_db()
        vp_data = fetch_updates()
        if vp_data and vp_data.get("updates"):
            updates = vp_data["updates"]
            timestamp = datetime.now(timezone.utc)
            
            # buckets for separating data
            price_changes = []
            player_statuses = []
            match_events = []
            bonus_points = []
            match_updates = []
            team_news = []
            
            for update in updates:
                # Add ingestion timestamp to all
                update["ingested_at"] = timestamp
                # Ensure 'timestamp' field exists using scraped date if available
                if "date" in update and update["date"]:
                     update["timestamp"] = timestamp 
                else:
                     update["timestamp"] = timestamp

                u_type = update.get("type")
                
                if u_type == "price_change":
                    price_changes.append(update)
                elif u_type == "status":
                    player_statuses.append(update)
                elif u_type in ["goal", "yellow_card", "red_card", "saves"]:
                    update["event_type"] = u_type
                    match_events.append(update)
                elif u_type == "bonus":
                    bonus_points.append(update)
                elif u_type == "match_update":
                    match_updates.append(update)
                elif u_type == "team_news":
                    team_news.append(update)

            # Insert into separate collections
            if price_changes:
                # Deduplicate price changes
                unique_prices = {}
                for p in price_changes:
                    unique_prices[p["player"]] = p
                
                deduped_price_changes = list(unique_prices.values())
                
                db.price_changes.delete_many({}) 
                db.price_changes.drop() 
                db.price_changes.insert_many(deduped_price_changes)
                logger.info(f"Examples: {deduped_price_changes[0]}")
                
            if player_statuses:
                db.player_status.drop()
                db.player_status.insert_many(player_statuses)
                
            if match_events:
                db.match_events.drop()
                db.match_events.insert_many(match_events)
                
            if bonus_points:
                db.bonus_points.drop()
                db.bonus_points.insert_many(bonus_points)
                
            if match_updates:
                db.match_updates.drop()
                db.match_updates.insert_many(match_updates)
                
            if team_news:
                db.team_news.drop()
                db.team_news.insert_many(team_news)
                
            logger.info(f"💾 Upserted Videoprinter data: {len(price_changes)} prices, {len(match_events)} events, {len(player_statuses)} statuses")
            
    except Exception as e:
        logger.error(f"Failed to update Videoprinter data: {e}")


if __name__ == "__main__":
    update_static_data()
