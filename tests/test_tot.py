from tot.mcts import MCTS, ThoughtNode
from tot.thoughts import score_thought


def test_ucb1_unvisited_node():
    """Unvisited nodes should always be selected first."""
    node = ThoughtNode(thought="test", score=0.0, visits=0)
    assert node.ucb1() == float("inf")
    print("✅ Unvisited node UCB1 = inf")


def test_ucb1_visited_node():
    """Visited nodes should have finite UCB1 score."""
    root = ThoughtNode(thought="root", score=1.0, visits=5)
    node = ThoughtNode(thought="child", score=3.0, visits=3, parent=root)
    score = node.ucb1()
    assert score != float("inf")
    assert score > 0
    print(f"✅ Visited node UCB1 = {score:.3f}")


def test_mcts_selects_best():
    """MCTS should select the highest scoring thought."""
    mcts = MCTS()
    thoughts = [
        "Step 1: Bad plan\nStep 2: Wrong\nStep 3: Fail\nStep 4: Give up",
        "Step 1: Compute matrix\nStep 2: Find eigenvalues\nStep 3: Verify\nStep 4: Done",
        "Step 1: Ok plan\nStep 2: Average\nStep 3: Fine\nStep 4: End",
    ]
    scores = [0.2, 0.9, 0.5]

    result = mcts.run(thoughts, scores)
    assert result["best_score"] > 0.5
    print(f"✅ MCTS selected best plan. Score: {result['best_score']:.3f}")


def test_score_thought_good_plan():
    """A good plan with math keywords should score high."""
    thought = """Step 1: Compute the matrix eigenvalues
Step 2: Solve the characteristic equation
Step 3: Calculate eigenvectors
Step 4: Verify results using Av=λv"""
    score = score_thought(thought, "eigenvalues")
    assert score >= 0.7
    print(f"✅ Good plan score: {score}")


def test_score_thought_bad_plan():
    """A bad plan should score low."""
    thought = "do something then do another thing"
    score = score_thought(thought, "eigenvalues")
    assert score <= 0.3
    print(f"✅ Bad plan score: {score}")