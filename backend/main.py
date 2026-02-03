"""
Main entry point for the BenchBoost FPL RAG Chatbot API.
This script is the single entry point that:
1. Loads environment variables and validates configuration
2. Warms the cache with FPL data on startup
3. Starts the background scheduler for automatic data refresh
4. Launches the FastAPI application via Uvicorn
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI
import uvicorn

# Import the FastAPI app factory from middleware
from backend.middleware.api import create_app
from backend.data import cache
from backend.scheduler import start_scheduler, stop_scheduler, warm_cache_on_startup

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def validate_environment():
    """Validate that required environment variables are set."""
    load_dotenv()

    required_vars = ["GOOGLE_API_KEY", "MONGO_URI"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please set them in your .env file")
        sys.exit(1)

    logger.info("Environment variables validated")


def initialize_cache():
    """Warm the cache with FPL data on startup."""
    logger.info("=" * 60)
    logger.info("Initializing FPL Chatbot Cache")
    logger.info("=" * 60)

    try:
        warm_cache_on_startup()
        stats = cache.get_cache_stats()
        logger.info(f"✅ Cache initialized: {stats.get('cache_size')} entries loaded")
        logger.info(f"   Hit rate: {stats.get('hit_rate_percent', 0)}%")
    except Exception as e:
        logger.error(f"❌ Error warming cache: {e}")
        logger.warning("⚠️ The API may have degraded performance until data is loaded.")


def initialize_scheduler():
    """Start the background scheduler for automatic data refresh."""
    try:
        start_scheduler(refresh_interval_hours=1)
        logger.info("✅ Background data refresh scheduler started (1 hour interval)")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")
        logger.warning(
            "⚠️ Automatic data refresh disabled. You may need to manually refresh data."
        )


def shutdown_scheduler():
    """Stop the background scheduler."""
    try:
        stop_scheduler()
        logger.info("Scheduler stopped")
    except Exception:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("Starting up FPL Chatbot API...")
    initialize_cache()
    initialize_scheduler()

    # Log final cache stats
    final_stats = cache.get_cache_stats()
    logger.info(f"Startup complete: {final_stats.get('cache_size')} entries in cache")

    yield

    # Shutdown
    logger.info("Shutting down FPL Chatbot API...")
    shutdown_scheduler()

    # Show final cache stats
    final_stats = cache.get_cache_stats()
    logger.info(
        f"Final cache stats: {final_stats.get('hit_rate_percent')}% hit rate, "
        f"{final_stats.get('total_requests')} total requests"
    )


# Create the FastAPI app at module level (required for reload to work)
# This must be done after imports but before main()
validate_environment()
app = create_app(lifespan=lifespan)


def main():
    """Main entry point - starts Uvicorn with the pre-created app."""
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("UVICORN_RELOAD", "false").lower() == "true"

    logger.info(f"Starting Uvicorn server on {host}:{port}")
    logger.info(f"Reload mode: {'enabled' if reload else 'disabled'}")

    # Start Uvicorn with import string to enable reload
    # When reload is enabled, uvicorn will reimport the module on changes
    uvicorn.run(
        "backend.main:app", host=host, port=port, reload=reload, log_level="info"
    )


if __name__ == "__main__":
    main()
