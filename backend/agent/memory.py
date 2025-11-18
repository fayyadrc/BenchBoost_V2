"""
Memory Management for BenchBoost FPL Chatbot

This module handles conversation history persistence across sessions.
Chat history is saved to disk and loaded on startup, allowing the agent
to "remember" previous conversations.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage


# Default memory file location
DEFAULT_MEMORY_FILE = Path.home() / ".benchboost" / "chat_history.json"


def serialize_message(message: BaseMessage) -> Dict[str, Any]:
    """Convert a LangChain message to a JSON-serializable dict."""
    return {
        "type": message.__class__.__name__,
        "content": message.content
    }


def deserialize_message(data: Dict[str, Any]) -> BaseMessage:
    """Convert a JSON dict back to a LangChain message."""
    msg_type = data.get("type")
    content = data.get("content", "")
    
    if msg_type == "HumanMessage":
        return HumanMessage(content=content)
    elif msg_type == "AIMessage":
        return AIMessage(content=content)
    else:
        # Default to HumanMessage if unknown
        return HumanMessage(content=content)


def load_chat_history(memory_file: Path = DEFAULT_MEMORY_FILE, max_messages: int = 100) -> List[BaseMessage]:
    """
    Load chat history from disk.
    
    Args:
        memory_file: Path to the JSON file containing chat history
        max_messages: Maximum number of messages to load (keeps recent ones)
    
    Returns:
        List of LangChain messages (HumanMessage, AIMessage)
    """
    if not memory_file.exists():
        print(f"No existing memory found at {memory_file}. Starting fresh.")
        return []
    
    try:
        with open(memory_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        messages = [deserialize_message(msg) for msg in data]
        
        # Keep only the most recent messages to avoid context overflow
        if len(messages) > max_messages:
            messages = messages[-max_messages:]
            print(f"Loaded {len(messages)} most recent messages (truncated from total).")
        else:
            print(f"Loaded {len(messages)} messages from previous sessions.")
        
        return messages
    
    except Exception as e:
        print(f"Error loading chat history: {e}")
        print("Starting with empty chat history.")
        return []


def save_chat_history(chat_history: List[BaseMessage], memory_file: Path = DEFAULT_MEMORY_FILE) -> None:
    """
    Save chat history to disk.
    
    Args:
        chat_history: List of LangChain messages to save
        memory_file: Path to the JSON file to save to
    """
    try:
        # Create directory if it doesn't exist
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Serialize messages
        data = [serialize_message(msg) for msg in chat_history]
        
        # Write to file
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Success message is only shown on explicit save or exit
        # print(f"Saved {len(chat_history)} messages to {memory_file}")
    
    except Exception as e:
        print(f"Error saving chat history: {e}")


def clear_chat_history(memory_file: Path = DEFAULT_MEMORY_FILE) -> None:
    """
    Clear (delete) the chat history file.
    
    Args:
        memory_file: Path to the JSON file to delete
    """
    try:
        if memory_file.exists():
            memory_file.unlink()
            print(f"Chat history cleared from {memory_file}")
        else:
            print("No chat history file to clear.")
    except Exception as e:
        print(f"Error clearing chat history: {e}")


def get_conversation_summary(chat_history: List[BaseMessage], max_pairs: int = 3) -> str:
    """
    Generate a brief summary of recent conversation for display.
    
    Args:
        chat_history: List of LangChain messages
        max_pairs: Number of recent Q&A pairs to include
    
    Returns:
        String summary of recent conversation
    """
    if not chat_history:
        return "No previous conversation."
    
    summary_lines = []
    # Process in pairs (Human, AI)
    for i in range(len(chat_history) - 1, -1, -2):
        if len(summary_lines) >= max_pairs:
            break
        
        if i >= 1:  # Ensure we have a pair
            human_msg = chat_history[i-1]
            ai_msg = chat_history[i]
            
            if isinstance(human_msg, HumanMessage) and isinstance(ai_msg, AIMessage):
                human_preview = human_msg.content[:50] + "..." if len(human_msg.content) > 50 else human_msg.content
                ai_preview = ai_msg.content[:50] + "..." if len(ai_msg.content) > 50 else ai_msg.content
                summary_lines.append(f"  Q: {human_preview}")
                summary_lines.append(f"  A: {ai_preview}")
    
    summary_lines.reverse()
    return "\n".join(summary_lines) if summary_lines else "No recent conversation."
