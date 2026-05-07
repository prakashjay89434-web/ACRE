from unittest.mock import patch
from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent
from agents.critic_agent import CriticAgent

MOCK_RAG = {
    "results": [{"text": "Eigenvalues satisfy Av=λv", "score": 0.8, "metadata": {}}],
    "best_score": 0.8,
    "attempts": 1,
    "queries_tried": ["test"]
}


def test_planner_returns_plan():
    with patch("agents.planner_agent.reflective_search", return_value=MOCK_RAG):
        agent = PlannerAgent()
        state = {"query": "Compute the eigenvalues of a 3x3 matrix"}
        result = agent(state)
    assert "plan" in result
    assert "steps" in result["plan"]
    assert len(result["plan"]["steps"]) > 0
    print("✅ Planner test passed")


def test_coder_returns_code_result():
    agent = CoderAgent()
    state = {
        "query": "Compute eigenvalues",
        "plan": {"steps": ["Step 1", "Step 2"], "estimated_difficulty": 0.5},
        "current_step": 0,
    }
    result = agent(state)
    assert "code_result" in result
    assert "code" in result["code_result"]
    assert "stdout" in result["code_result"]
    print("✅ Coder test passed")


def test_critic_returns_verification():
    agent = CriticAgent()
    state = {
        "query": "Compute eigenvalues",
        "plan": {"steps": ["Step 1"]},
        "code_result": {
            "code": "print(42)",
            "stdout": "42",
            "stderr": "",
            "error": False,
            "confidence": 0.9,
        },
    }
    result = agent(state)
    assert "verification" in result
    assert 0 <= result["verification"]["score"] <= 100
    print("✅ Critic test passed")


def test_full_pipeline():
    with patch("agents.planner_agent.reflective_search", return_value=MOCK_RAG):
        planner = PlannerAgent()
        coder = CoderAgent()
        critic = CriticAgent()

        state = {"query": "Solve: x^2 - 5x + 6 = 0"}

        print("\n--- Running full pipeline ---")
        state = planner(state)
        state = coder(state)
        state = critic(state)

        assert "query" in state
        assert "plan" in state
        assert "code_result" in state
        assert "verification" in state
        assert "error" not in state
        print(f"✅ Full pipeline passed. Score: {state['verification']['score']}/100")