from collections import deque
from typing import Optional


class ConversationMemory:
    """
    Sliding window conversation memory.
    Stores last N exchanges between user and assistant.
    """

    def __init__(self, max_exchanges: int = 5):
        self.max_exchanges = max_exchanges
        self.history = deque(maxlen=max_exchanges * 2)  # user + assistant pairs

    def add_user_message(self, message: str):
        self.history.append({"role": "user", "content": message})

    def add_assistant_message(self, message: str):
        self.history.append({"role": "assistant", "content": message})

    def get_context(self) -> str:
        """Return conversation history as formatted string."""
        if not self.history:
            return ""

        context = "Previous conversation:\n"
        for msg in self.history:
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content'][:200]}\n"
        return context

    def get_messages(self) -> list:
        """Return history as list of messages."""
        return list(self.history)

    def clear(self):
        self.history.clear()

    def is_empty(self) -> bool:
        return len(self.history) == 0


# Global memory instance
memory = ConversationMemory(max_exchanges=5)