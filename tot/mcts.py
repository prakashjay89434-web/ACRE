import math
import random
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ThoughtNode:
    """
    A single node in the Tree of Thoughts.
    
    WHY DATACLASS:
    - Clean, readable structure
    - Each node = one candidate plan
    - Tracks visits and value for UCB1
    """
    thought: str
    score: float = 0.0
    visits: int = 0
    parent: Optional["ThoughtNode"] = None
    children: list["ThoughtNode"] = field(default_factory=list)

    def ucb1(self, exploration: float = 1.414) -> float:
        """
        UCB1 formula: balances exploitation vs exploration.
        
        score/visits = exploitation (how good is this node?)
        sqrt(log(parent_visits)/visits) = exploration (how little visited?)
        
        exploration constant 1.414 = sqrt(2) — standard value
        """
        if self.visits == 0:
            return float("inf")  # Always explore unvisited nodes first

        parent_visits = self.parent.visits if self.parent else self.visits
        exploitation = self.score / self.visits
        exploration_term = exploration * math.sqrt(
            math.log(parent_visits) / self.visits
        )
        return exploitation + exploration_term

    def update(self, reward: float):
        """Backpropagate reward up the tree."""
        self.visits += 1
        self.score += reward
        if self.parent:
            self.parent.update(reward)


class MCTS:
    """
    Monte Carlo Tree Search for plan selection.
    
    For ACRE we use a simplified version:
    - No rollouts (too slow with LLM)
    - Direct scoring of thoughts
    - UCB1 for selection
    """

    def __init__(self, exploration: float = 1.414):
        self.exploration = exploration

    def select_best(self, nodes: list[ThoughtNode]) -> ThoughtNode:
        """Select node with highest UCB1 score."""
        return max(nodes, key=lambda n: n.ucb1(self.exploration))

    def run(self, thoughts: list[str], scores: list[float]) -> dict:
        """
        Given a list of thoughts and their scores,
        use MCTS to select the best one.
        
        Returns the best thought with reasoning.
        """
        if not thoughts:
            return {"best_thought": "", "best_score": 0.0, "reasoning": "No thoughts"}

        root = ThoughtNode(thought="root", score=0.0, visits=1)

        nodes = []
        for i, (thought, score) in enumerate(zip(thoughts, scores)):
            node = ThoughtNode(
                thought=thought,
                score=score,
                visits=1,
                parent=root
            )
            root.children.append(node)
            nodes.append(node)

        # Run 10 MCTS iterations
        for _ in range(10):
            selected = self.select_best(nodes)
            # Simulate: add small random noise to explore
            reward = selected.score + random.uniform(-0.05, 0.05)
            reward = max(0.0, min(1.0, reward))
            selected.update(reward)

        # Pick the node with highest average score
        best = max(nodes, key=lambda n: n.score / n.visits if n.visits > 0 else 0)

        return {
            "best_thought": best.thought,
            "best_score": best.score / best.visits,
            "all_scores": [
                {
                    "thought": n.thought[:80],
                    "avg_score": round(n.score / n.visits, 3),
                    "visits": n.visits
                }
                for n in nodes
            ]
        }