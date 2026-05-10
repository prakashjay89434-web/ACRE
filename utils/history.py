import json
import os
from datetime import datetime


HISTORY_FILE = "data/chat_history.json"


def load_history() -> list:
    """Load all chat history from file."""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_conversation(query: str, answer: str, query_type: str = "general"):
    """Save a single conversation to history."""
    history = load_history()
    
    history.append({
        "id": len(history) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "query": query,
        "answer": answer[:500],  # Save first 500 chars
        "type": query_type
    })
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def get_history() -> list:
    """Return all history."""
    return load_history()


def clear_history():
    """Clear all history."""
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)