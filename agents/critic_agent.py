from agents.base_agent import BaseAgent
from sandbox.math_checker import run_all_checks
from typing import Any


class CriticAgent(BaseAgent):

    def __init__(self):
        super().__init__(name="CriticAgent")

    def get_name(self) -> str:
        return self.name

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        code_result = state.get("code_result", {})
        stdout = code_result.get("stdout", "")
        stderr = code_result.get("stderr", "")
        error = code_result.get("error", True)

        print(f"  [Critic] Running math verification...")

        verification = run_all_checks(stdout, stderr, error)

        print(f"  [Critic] Score: {verification['score']}/100")
        print(f"  [Critic] Checks: {verification['checks']}")

        return {**state, "verification": verification}