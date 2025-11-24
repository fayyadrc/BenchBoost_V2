"""
Main entry point for the BenchBoost FPL RAG Chatbot.
This script does four things:
1.  Warms the cache with FPL data on startup.
2.  Starts the background scheduler for automatic data refresh.
3.  Loads conversation history from previous sessions.
4.  Starts the chatbot agent loop.
"""

import os
import logging
from dotenv import load_dotenv

from .agent.agent import create_agent, run_chat_loop
from .agent.memory import load_chat_history, save_chat_history, get_conversation_summary
from .data.cache import load_core_game_data, get_cache_stats
from .scheduler import start_scheduler, stop_scheduler, warm_cache_on_startup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found. Please set it in a .env file.")
        return

    # --- 1. WARM CACHE ON STARTUP ---
    # Pre-populate cache with frequently accessed data
    logger.info("=" * 60)
    logger.info("Starting BenchBoost FPL Chatbot")
    logger.info("=" * 60)
    
    try:
        warm_cache_on_startup()
        stats = get_cache_stats()
        logger.info(f"Cache initialized: {stats.get('cache_size')} entries loaded")
    except Exception as e:
        logger.error(f"Error warming cache: {e}")
        logger.warning("The chatbot may have degraded performance.")
    
    # --- 2. START BACKGROUND SCHEDULER ---
    # Automatically refresh data every hour
    try:
        start_scheduler(refresh_interval_hours=1)
        logger.info("Background data refresh scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        logger.warning("Automatic data refresh disabled. You may need to manually refresh.")
    
    # (Note: The vector DB is loaded by a separate script, load_vector_db.py)

    # --- 3. LOAD CONVERSATION MEMORY ---
    # Load chat history from previous sessions
    chat_history = load_chat_history()
    
    if chat_history:
        print("\n📚 Resuming from previous conversation:")
        print(get_conversation_summary(chat_history))
    
    # --- 4. START CHATBOT ---
    # Create the agent and start the chat loop
    agent_executor = create_agent()
    
    try:
        run_chat_loop(agent_executor, chat_history)
    finally:
        # Save chat history when exiting (even if interrupted)
        save_chat_history(chat_history)
        print("\n💾 Conversation saved.")
        
        # Stop scheduler
        try:
            stop_scheduler()
            logger.info("Scheduler stopped")
        except Exception:
            pass
        
        # Show final cache stats
        final_stats = get_cache_stats()
        logger.info(f"Final cache stats: {final_stats.get('hit_rate_percent')}% hit rate, "
                   f"{final_stats.get('total_requests')} total requests")
        
        print("See you next time!")

if __name__ == "__main__":
    main()