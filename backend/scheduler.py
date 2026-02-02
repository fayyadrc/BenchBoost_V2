"""
Background Scheduler for Automatic FPL Data Refresh

Automatically refreshes FPL data at configured intervals to ensure
the cache and database stay up-to-date without manual intervention.
"""

import sys
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.append(project_root)

from backend.data import cache
from backend.database.ingestion import update_static_data, update_videoprinter_data

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: BackgroundScheduler | None = None


def refresh_fpl_data():
    """
    Refresh all FPL data (cache + database).
    
    This function:
    1. Invalidates the cache
    2. Runs database ingestion
    3. Reloads core game data into cache
    """
    logger.info("=" * 60)
    logger.info("Starting scheduled FPL data refresh...")
    logger.info(f"Time: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    try:
        # Step 1: Invalidate cache
        logger.info("Invalidating cache...")
        cache.invalidate_cache()
        
        # Step 2: Update database
        logger.info("Updating database...")
        update_static_data()
        
        # Step 3: Warm cache
        logger.info("Warming cache...")
        cache.load_core_game_data(force_refresh=True)
        
        # Log cache stats
        stats = cache.get_cache_stats()
        logger.info(f"Cache warmed: {stats.get('cache_size')} entries")
        
        logger.info("=" * 60)
        logger.info("✅ Scheduled data refresh complete!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Scheduled data refresh failed: {e}", exc_info=True)


def start_scheduler(
    refresh_interval_hours: int = 1,
    enable_cron: bool = False,
    cron_expression: str = "0 */1 * * *"  # Every hour on the hour
):
    """
    Start the background scheduler for automatic data refresh.
    
    Args:
        refresh_interval_hours: Refresh interval in hours (default: 1)
        enable_cron: Use cron expression instead of interval (default: False)
        cron_expression: Cron expression for scheduling (default: every hour)
        
    Returns:
        BackgroundScheduler instance
    """
    global _scheduler
    
    if _scheduler is not None and _scheduler.running:
        logger.warning("Scheduler is already running")
        return _scheduler
    
    _scheduler = BackgroundScheduler()
    
    if enable_cron:
        # Use cron trigger
        trigger = CronTrigger.from_crontab(cron_expression)
        _scheduler.add_job(
            refresh_fpl_data,
            trigger=trigger,
            id="fpl_data_refresh",
            name="FPL Data Refresh (Cron)",
            replace_existing=True
        )
        logger.info(f"Scheduler started with cron: {cron_expression}")
    else:
        # Use interval trigger
        _scheduler.add_job(
            refresh_fpl_data,
            'interval',
            hours=refresh_interval_hours,
            id="fpl_data_refresh",
            name="FPL Data Refresh (Interval)",
            replace_existing=True
        )
        logger.info(f"Scheduler started with interval: {refresh_interval_hours} hours")
        
        # Add separate job for Videoprinter updates (every 15 minutes for real-time updates)
        _scheduler.add_job(
            update_videoprinter_data,
            'interval',
            minutes=15,
            id="fpl_videoprinter_refresh",
            name="Videoprinter Update (Interval)",
            replace_existing=True
        )
        logger.info("Scheduler added Videoprinter update job (every 15 minutes)")
    
    _scheduler.start()
    logger.info("Background scheduler is running")
    
    return _scheduler


def stop_scheduler():
    """Stop the background scheduler."""
    global _scheduler
    
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown()
        logger.info("Scheduler stopped")
        _scheduler = None
    else:
        logger.warning("Scheduler is not running")


def get_scheduler() -> BackgroundScheduler | None:
    """Get the current scheduler instance."""
    return _scheduler


def warm_cache_on_startup():
    """
    Warm the cache on application startup.
    
    This should be called when the application starts to pre-populate
    the cache with frequently accessed data.
    """
    logger.info("Warming cache on startup...")
    
    try:
        cache.load_core_game_data(force_refresh=True)
        stats = cache.get_cache_stats()
        logger.info(f"✅ Cache warmed: {stats.get('cache_size')} entries loaded")
    except Exception as e:
        logger.error(f"❌ Failed to warm cache: {e}", exc_info=True)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Warm cache on startup
    warm_cache_on_startup()
    
    # Start scheduler (refresh every hour)
    start_scheduler(refresh_interval_hours=1)
    
    # Keep the script running
    try:
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        stop_scheduler()
