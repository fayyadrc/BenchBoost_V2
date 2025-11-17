"""
Main entry point for the BenchBoost FPL RAG Chatbot.

This script does two things:
1.  Loads the FPL data into the in-memory cache ("Pre-production").
2.  Starts the chatbot agent loop ("In Production").
"""

import os
from dotenv import load_dotenv

# Import our custom modules
from fplAI.data.cache import load_core_game_data
from fplAI.agent.agent_creator import create_agent, run_chat_loop

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

    # --- 2. IN PRODUCTION ---
    # Create the agent and an empty chat history
    agent_executor = create_agent()
    chat_history = []
    
    # Start the agent and the chat loop
    run_chat_loop(agent_executor, chat_history)

if __name__ == "__main__":
    main()