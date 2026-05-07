import ollama
from rag.ingestion import search


RELEVANCE_THRESHOLD = 0.4
MAX_RETRIES = 2


def score_relevance(query: str, results: list[dict]) -> float:
    """Average cosine similarity score of top results."""
    if not results:
        return 0.0
    return sum(r["score"] for r in results) / len(results)


def rewrite_query(original_query: str, attempt: int) -> str:
    """Use LLM to rewrite query for better retrieval."""
    prompt = f"""Rewrite this search query to find more relevant information.
Original query: {original_query}
Attempt: {attempt}
Rules:
- Make it more specific
- Use different keywords
- Keep it under 20 words
- Return ONLY the rewritten query, nothing else"""

    response = ollama.chat(
        model="qwen2.5-coder:1.5b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.message.content.strip()


def reflective_search(query: str, top_k: int = 3) -> dict:
    """
    Self-reflective RAG:
    1. Search
    2. Score results
    3. If score low → rewrite query → search again
    4. Return best results
    """
    attempts = []
    current_query = query
    best_results = []
    best_score = 0.0

    for attempt in range(MAX_RETRIES + 1):
        print(f"  [RAG] Attempt {attempt + 1}: '{current_query[:50]}'")

        results = search(current_query, top_k=top_k)
        score = score_relevance(current_query, results)

        print(f"  [RAG] Relevance score: {score:.3f}")

        attempts.append({
            "query": current_query,
            "score": score,
            "results": results
        })

        if score > best_score:
            best_score = score
            best_results = results

        if score >= RELEVANCE_THRESHOLD:
            print(f"  [RAG] Good results found. Stopping.")
            break

        if attempt < MAX_RETRIES:
            print(f"  [RAG] Score too low. Rewriting query...")
            current_query = rewrite_query(query, attempt + 1)

    return {
        "results": best_results,
        "best_score": best_score,
        "attempts": len(attempts),
        "queries_tried": [a["query"] for a in attempts]
    }