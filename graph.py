from langgraph.graph import StateGraph, END
from typing import TypedDict, Any
from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent
from agents.critic_agent import CriticAgent
from agents.general_agent import GeneralAgent
from agents.system_agent import SystemAgent
from agents.project_builder_agent import ProjectBuilderAgent
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
system = SystemAgent()
project = ProjectBuilderAgent()


def route_query(state: dict) -> str:
    query_type = classify_query(state["query"])
    state["query_type"] = query_type
    print(f"  [Router] Query type: {query_type}")
    return query_type


def build_graph():
    graph = StateGraph(ACREState)

    graph.add_node("planner", planner)
    graph.add_node("coder", coder)
    graph.add_node("critic", critic)
    graph.add_node("general", general)
    graph.add_node("system", system)
    graph.add_node("project", project)

    graph.set_conditional_entry_point(
        route_query,
        {
            "technical": "planner",
            "general": "general",
            "system": "system",
            "project": "project"
        }
    )

    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "critic")
    graph.add_edge("critic", END)
    graph.add_edge("general", END)
    graph.add_edge("system", END)
    graph.add_edge("project", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    print("=== Testing Project Builder ===")
    result = app.invoke({
        "query": "build a todo app with flask",
        "plan": {}, "current_step": 0,
        "code_result": {}, "verification": {},
        "error": "", "query_type": ""
    })
    print(result['code_result']['stdout'])