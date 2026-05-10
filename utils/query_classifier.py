import ollama


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
    "is modi", "is elon", "is trump", "about modi",
    "about elon", "tell about", "batao", "bताओ"
]


def classify_query(query: str) -> str:
    query_lower = query.lower()

    # Check general keywords first
    for kw in GENERAL_KEYWORDS:
        if kw in query_lower:
            return "general"

    # Check technical keywords
    for kw in TECHNICAL_KEYWORDS:
        if kw in query_lower:
            return "technical"

    # If still uncertain use a simple heuristic
    # Queries with numbers/symbols = technical
    import re
    if re.search(r'[\d\+\-\*\/\^\=\(\)\[\]]', query):
        return "technical"

    # Default = general
    return "general"


if __name__ == "__main__":
    tests = [
        "Who is Elon Musk?",
        "Calculate eigenvalues of a matrix",
        "Kal ka mausam kaisa hoga?",
        "Solve x^2 - 5x + 6 = 0",
        "Chicken biryani kaise banate hain?",
        "Write a fibonacci function",
        "Modi kaun hai?",
        "What is machine learning?",
        "2 + 2 = ?",
        "Tell me about India",
    ]

    for t in tests:
        result = classify_query(t)
        print(f"{result:10} → {t}")