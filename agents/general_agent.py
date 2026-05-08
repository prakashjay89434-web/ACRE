from agents.base_agent import BaseAgent
from utils.web_search import search_web
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

        # Search web for context
        print(f"  [General] Searching web...")
        web_results = search_web(query, max_results=3)

        # Use LLM to summarize web results
        prompt = f"""Answer this question clearly and concisely using the web search results below.

Question: {query}

Web Search Results:
{web_results}

Give a clear, direct answer in 3-5 sentences. Do not write code."""

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.message.content.strip()
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