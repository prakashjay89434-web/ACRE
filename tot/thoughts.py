import ollama


def generate_thoughts(query: str, context: str, n: int = 3) -> list[str]:
    """
    Generate n different plans for the same query.
    Each plan is a different approach — different strategy.
    """
    thoughts = []

    prompts = [
        f"Plan approach 1 (analytical): Break this into 4 mathematical steps: {query}",
        f"Plan approach 2 (code-first): Break this into 4 programming steps: {query}",
        f"Plan approach 3 (verification-focused): Break this into 4 steps focusing on correctness: {query}",
    ]

    for i, prompt in enumerate(prompts[:n]):
        full_prompt = f"""{prompt}

Context: {context if context else 'No context'}

Reply with exactly 4 steps, one per line, starting with Step 1:, Step 2:, Step 3:, Step 4:
Keep each step under 15 words."""

        response = ollama.chat(
            model="qwen2.5-coder:1.5b",
            messages=[{"role": "user", "content": full_prompt}]
        )

        raw = response.message.content
        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        steps = [l for l in lines if l.startswith("Step")]

        if not steps:
            steps = lines[:4]

        thought = "\n".join(steps)
        thoughts.append(thought)
        print(f"  [ToT] Generated approach {i + 1}")

    return thoughts


def score_thought(thought: str, query: str) -> float:
    """
    Score a thought/plan from 0.0 to 1.0.
    
    Heuristic scoring based on:
    - Has 4 steps (0.3)
    - Contains math keywords (0.3)
    - Contains verification step (0.2)
    - Reasonable length (0.2)
    """
    score = 0.0
    thought_lower = thought.lower()

    # Check step count
    step_count = sum(1 for line in thought.split("\n") if line.strip().startswith("Step"))
    if step_count >= 4:
        score += 0.3
    elif step_count >= 2:
        score += 0.15

    # Check math keywords
    math_keywords = ["matrix", "equation", "calculate", "compute",
                     "solve", "derivative", "integral", "vector",
                     "eigenvalue", "gradient", "function"]
    if any(kw in thought_lower for kw in math_keywords):
        score += 0.3

    # Check verification step
    verify_keywords = ["verify", "check", "validate", "test", "confirm"]
    if any(kw in thought_lower for kw in verify_keywords):
        score += 0.2

    # Check reasonable length
    if 50 < len(thought) < 500:
        score += 0.2

    return round(score, 3)