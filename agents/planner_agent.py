from agents.base_agent import BaseAgent
from rag.reflection import reflective_search
from tot.thoughts import generate_thoughts, score_thought
from tot.mcts import MCTS
from typing import Any


class PlannerAgent(BaseAgent):

    def __init__(self):
        super().__init__(name="PlannerAgent")
        self.mcts = MCTS(exploration=1.414)

    def get_name(self) -> str:
        return self.name

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        query = state.get("query", "")
        print(f"  [Planner] Thinking about: '{query}'")

        # Step 1: RAG retrieval
        print(f"  [Planner] Searching knowledge base...")
        rag_result = reflective_search(query, top_k=2)
        context = "\n".join([r["text"] for r in rag_result["results"]])

        # Step 2: Generate 3 different plans (Tree of Thoughts)
        print(f"  [Planner] Generating 3 thought branches...")
        thoughts = generate_thoughts(query, context, n=3)

        # Step 3: Score each plan
        scores = [score_thought(t, query) for t in thoughts]
        print(f"  [Planner] Scores: {scores}")

        # Step 4: MCTS selects best plan
        mcts_result = self.mcts.run(thoughts, scores)
        best_plan = mcts_result["best_thought"]

        print(f"  [Planner] Best plan score: {mcts_result['best_score']:.3f}")

        # Parse steps from best plan
        lines = [l.strip() for l in best_plan.split("\n") if l.strip()]
        steps = [l for l in lines if l.startswith("Step")]
        if not steps:
            steps = lines[:4]

        plan = {
            "steps": steps,
            "estimated_difficulty": 1 - mcts_result["best_score"],
            "rag_context": context,
            "rag_score": rag_result["best_score"],
            "mcts_score": mcts_result["best_score"],
            "all_approaches": mcts_result["all_scores"]
        }

        print(f"  [Planner] Selected plan with {len(steps)} steps")
        return {**state, "plan": plan, "current_step": 0}