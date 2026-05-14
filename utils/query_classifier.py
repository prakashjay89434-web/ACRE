TECHNICAL_KEYWORDS = [
    "calculate", "compute", "solve", "matrix", "eigenvalue",
    "determinant", "derivative", "integral", "gradient",
    "factorial", "fibonacci", "prime", "algorithm",
    "code", "program", "function", "python", "implement",
    "sort", "search", "binary", "recursion", "equation",
    "polynomial", "vector", "linear algebra", "calculus"
]

GENERAL_KEYWORDS = [
    "who is", "who was", "what is", "where is", "when did",
    "why did", "how did", "tell me", "explain", "describe",
    "history", "biography", "meaning", "definition",
    "kaun hai", "kya hai", "kaise", "kyun", "kab",
    "mausam", "recipe", "khana", "movie", "news",
    "who are", "what are", "which is", "which are",
    "tell about", "batao"
]

SYSTEM_KEYWORDS = [
    "open", "launch", "start", "close", "shut down",
    "restart", "kholo", "band karo", "open chrome",
    "open notepad", "open calculator", "open vs code",
    "take screenshot", "screenshot lo", "type",
    "open terminal", "open cmd"
]


def classify_query(query: str) -> str:
    query_lower = query.lower()

    # Check system commands first
    for kw in SYSTEM_KEYWORDS:
        if kw in query_lower:
            return "system"

    # Check general keywords
    for kw in GENERAL_KEYWORDS:
        if kw in query_lower:
            return "general"

    # Check technical keywords
    for kw in TECHNICAL_KEYWORDS:
        if kw in query_lower:
            return "technical"

    import re
    if re.search(r'[\d\+\-\*\/\^\=\(\)\[\]]', query):
        return "technical"

    return "general"


if __name__ == "__main__":
    tests = [
        "open chrome",
        "Who is Elon Musk?",
        "Calculate eigenvalues",
        "take screenshot",
        "open vs code",
        "Solve x^2 - 5x + 6 = 0",
    ]
    for t in tests:
        print(f"{classify_query(t):10} → {t}")