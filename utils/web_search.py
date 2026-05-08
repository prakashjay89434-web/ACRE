from ddgs import DDGS


def search_web(query: str, max_results: int = 3) -> str:
    """
    Search the web using DuckDuckGo and return summarized results.
    No API key needed — completely free and local.
    """
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "url": r.get("href", "")
                })

        if not results:
            return "No results found."

        # Format results
        formatted = ""
        for i, r in enumerate(results, 1):
            formatted += f"Result {i}: {r['title']}\n"
            formatted += f"{r['body']}\n"
            formatted += f"Source: {r['url']}\n\n"

        return formatted

    except Exception as e:
        return f"Search failed: {str(e)}"


if __name__ == "__main__":
    # Test
    result = search_web("What is Python programming language")
    print(result)