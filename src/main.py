"""
Main entry point for the BenchBoost FPL RAG Chatbot.

This script does three things:
1.  Loads the FPL data into the in-memory cache ("Pre-production").
2.  Loads conversation history from previous sessions.
3.  Starts the chatbot agent loop ("In Production").
"""

import os
from dotenv import load_dotenv

# Import our custom modules (relative to `src/` package root)
from .agent.agent import create_agent, run_chat_loop
from .agent.memory import load_chat_history, save_chat_history, get_conversation_summary
from .data.cache import load_core_game_data

def main():
    # Load environment variables (like GOOGLE_API_KEY) from .env file
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found. Please set it in a .env file.")
        return

    # --- 1. PRE-PRODUCTION ---
    # Load all FPL data into the cache (core_data dictionary)
    try:
        load_core_game_data()
    except Exception as e:
        print(f"Error loading FPL game data: {e}")
        print("The chatbot may not have access to player/team data.")
        # Depending on requirements, you might want to exit here
        # return 
    
    # (Note: The vector DB is loaded by a separate script, load_vector_db.py)

    # --- 2. LOAD CONVERSATION MEMORY ---
    # Load chat history from previous sessions
    chat_history = load_chat_history()
    
    if chat_history:
        print("\n📚 Resuming from previous conversation:")
        print(get_conversation_summary(chat_history))
    
    # --- 3. IN PRODUCTION ---
    # Create the agent and start the chat loop
    agent_executor = create_agent()
    
    try:
        run_chat_loop(agent_executor, chat_history)
    finally:
        # Save chat history when exiting (even if interrupted)
        save_chat_history(chat_history)
        print("\n💾 Conversation saved. See you next time!")

if __name__ == "__main__":
    main()