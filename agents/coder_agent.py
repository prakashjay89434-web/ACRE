from agents.base_agent import BaseAgent
from sandbox.executor import run_code
from typing import Any
import ollama


class CoderAgent(BaseAgent):

    def __init__(self):
        super().__init__(name="CoderAgent")
        self.model = "qwen2.5-coder:1.5b"

    def get_name(self) -> str:
        return self.name

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        plan = state.get("plan", {})
        steps = plan.get("steps", [])
        query = state.get("query", "")
        print(f"  [Coder] Generating code for: '{query}'")

        prompt = f"""Write Python code to solve this task: {query}
        
Rules:
- Only use: numpy, scipy, sympy, pandas, math, random
- Print the final result
- No explanations, just code
- Code must be complete and runnable"""

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.message.content

        # Extract code from markdown if present
        if "```python" in raw:
            code = raw.split("```python")[1].split("```")[0].strip()
        elif "```" in raw:
            code = raw.split("```")[1].split("```")[0].strip()
        else:
            code = raw.strip()

        print(f"  [Coder] Executing code in sandbox...")
        result = run_code(code, timeout=30)

        if result["error"]:
            print(f"  [Coder] Error: {result['stderr'][:100]}")
        else:
            print(f"  [Coder] Success. Output: {result['stdout'][:100]}")

        return {
            **state,
            "code_result": {
                "code": code,
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "error": result["error"],
                "confidence": 0.9 if not result["error"] else 0.2,
            }
        }