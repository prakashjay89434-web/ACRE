from langgraph.graph import StateGraph, END
from typing import TypedDict, Any
from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent
from agents.critic_agent import CriticAgent


# Define the shared state structure
class ACREState(TypedDict):
    query: str
    plan: dict
    current_step: int
    code_result: dict
    verification: dict
    error: str


# Instantiate agents
planner = PlannerAgent()
coder = CoderAgent()
critic = CriticAgent()


# Build the graph
def build_graph():
    graph = StateGraph(ACREState)

    # Add nodes
    graph.add_node("planner", planner)
    graph.add_node("coder", coder)
    graph.add_node("critic", critic)

    # Define flow: planner -> coder -> critic -> END
    graph.set_entry_point("planner")
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "critic")
    graph.add_edge("critic", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    result = app.invoke({
        "query": "Calculate the eigenvalues of a 3x3 matrix",
        "plan": {},
        "current_step": 0,
        "code_result": {},
        "verification": {},
        "error": ""
    })

    print("\n--- FINAL RESULT ---")
    print(f"Query: {result['query']}")
    print(f"Plan steps: {result['plan']['steps']}")
    print(f"Code output: {result['code_result']['stdout']}")
    print(f"Verification score: {result['verification']['score']}/100")