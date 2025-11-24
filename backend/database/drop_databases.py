import sys
import os
import logging
import time

# --- Path Setup ---
# Add the project root to sys.path to allow imports from backend.*
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(project_root)

# --- Imports ---
from backend.database.db import get_db

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def drop_all_collections():
    """
    Drops all FPL-related collections from the database.
    Collections: players, teams, gameweeks, fixtures
    """
    start_time = time.time()
    logger.info("🗑️  Starting Database Cleanup...")

    try:
        db = get_db()
        
        collections_to_drop = ["players", "teams", "gameweeks", "fixtures"]
        
        for collection_name in collections_to_drop:
            logger.info(f"🔥 Dropping collection: {collection_name}...")
            db[collection_name].drop()
            
        elapsed = time.time() - start_time
        logger.info(f"✅ Database cleanup complete in {elapsed:.2f} seconds.")

    except Exception as e:
        logger.error(f"❌ Database cleanup failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Optional: Add a confirmation prompt to prevent accidental deletion
    confirm = input("⚠️  Are you sure you want to DROP ALL databases? This action is irreversible. (yes/no): ")
    if confirm.lower() == "yes":
        drop_all_collections()
    else:
        logger.info("🚫 Operation cancelled.")
