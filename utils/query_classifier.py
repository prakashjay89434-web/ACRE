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
    "open", "launch", "start", "close",
    "kholo", "band karo", "open chrome",
    "open notepad", "open calculator", "open vs code",
    "take screenshot", "screenshot lo",
    "open terminal", "open cmd", "open youtube",
    "open whatsapp", "open google", "search on youtube",
    "search on google", "send message", "send email"
]

PROJECT_KEYWORDS = [
    "build", "create a project", "make a project",
    "build a", "create a", "make a",
    "develop", "scaffold", "generate project",
    "new project", "setup project"
]


def classify_query(query: str) -> str:
    query_lower = query.lower()

    # Check project builder first
    for kw in PROJECT_KEYWORDS:
        if kw in query_lower:
            return "project"

    # Check system commands
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
        "build a todo app with flask",
        "open youtube",
        "who is elon musk",
        "calculate eigenvalues",
        "create a REST API",
        "make a weather app",
    ]
    for t in tests:
        print(f"{classify_query(t):10} → {t}")