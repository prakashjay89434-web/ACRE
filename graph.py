from langgraph.graph import StateGraph, END
from typing import TypedDict, Any
from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent
from agents.critic_agent import CriticAgent
from agents.general_agent import GeneralAgent
from utils.query_classifier import classify_query


class ACREState(TypedDict):
    query: str
    plan: dict
    current_step: int
    code_result: dict
    verification: dict
    error: str
    query_type: str


planner = PlannerAgent()
coder = CoderAgent()
critic = CriticAgent()
general = GeneralAgent()


def route_query(state: dict) -> str:
    """Route to technical or general pipeline."""
    query_type = classify_query(state["query"])
    state["query_type"] = query_type
    print(f"  [Router] Query type: {query_type}")
    return query_type


def build_graph():
    graph = StateGraph(ACREState)

    # Add nodes
    graph.add_node("planner", planner)
    graph.add_node("coder", coder)
    graph.add_node("critic", critic)
    graph.add_node("general", general)

    # Router as entry point
    graph.set_conditional_entry_point(
        route_query,
        {
            "technical": "planner",
            "general": "general"
        }
    )

    # Technical pipeline
    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "critic")
    graph.add_edge("critic", END)

    # General pipeline
    graph.add_edge("general", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    # Test general query
    print("=== Testing General Query ===")
    result = app.invoke({
        "query": "Who is Elon Musk?",
        "plan": {}, "current_step": 0,
        "code_result": {}, "verification": {},
        "error": "", "query_type": ""
    })
    print(f"Answer: {result['code_result']['stdout'][:300]}")

    print("\n=== Testing Technical Query ===")
    result = app.invoke({
        "query": "Calculate eigenvalues of a 3x3 matrix",
        "plan": {}, "current_step": 0,
        "code_result": {}, "verification": {},
        "error": "", "query_type": ""
    })
    print(f"Output: {result['code_result']['stdout'][:200]}")