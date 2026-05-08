from agents.base_agent import BaseAgent
from utils.web_search import search_web
from utils.memory import memory
from typing import Any
import ollama


class GeneralAgent(BaseAgent):

    def __init__(self):
        super().__init__(name="GeneralAgent")
        self.model = "qwen2.5-coder:1.5b"

    def get_name(self) -> str:
        return self.name

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        query = state.get("query", "")
        print(f"  [General] Answering: '{query}'")

        # Get conversation history
        conversation_context = memory.get_context()

        # Search web for context
        print(f"  [General] Searching web...")
        web_results = search_web(query, max_results=3)

        # Use LLM to answer with memory
        prompt = f"""You are a helpful AI assistant. Answer clearly and concisely.

{conversation_context}

Web Search Results:
{web_results}

Current Question: {query}

Give a clear, direct answer in 3-5 sentences. Use conversation history if relevant."""

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.message.content.strip()

        # Save to memory
        memory.add_user_message(query)
        memory.add_assistant_message(answer)

        print(f"  [General] Answer ready")

        return {
            **state,
            "code_result": {
                "code": "",
                "stdout": answer,
                "stderr": "",
                "error": False,
                "confidence": 0.9,
            }
        }