from unittest.mock import patch
from rag.reflection import score_relevance, reflective_search


def test_score_relevance_empty():
    score = score_relevance("test query", [])
    assert score == 0.0
    print("✅ Empty results score 0.0")


def test_score_relevance_with_results():
    mock_results = [
        {"text": "Eigenvalues satisfy Av=λv", "score": 0.8, "metadata": {}},
        {"text": "Matrix decomposition", "score": 0.6, "metadata": {}},
    ]
    score = score_relevance("eigenvalues", mock_results)
    assert score == 0.7
    print(f"✅ Score calculated correctly: {score}")


def test_reflective_search_finds_results():
    """
    Mock the search function so we don't need
    real Qdrant data for this test.
    """
    mock_results = [
        {"text": "Eigenvalues are scalar values", "score": 0.85, "metadata": {}},
        {"text": "Matrix characteristic polynomial", "score": 0.75, "metadata": {}},
    ]

    with patch("rag.reflection.search", return_value=mock_results):
        result = reflective_search("eigenvalues of a matrix", top_k=2)

    assert len(result["results"]) > 0
    assert result["best_score"] > 0.4
    assert result["attempts"] == 1
    print(f"✅ Reflective search passed. Score: {result['best_score']:.3f}")


def test_reflective_search_retries_on_low_score():
    """If first search returns low score, it should retry."""
    low_results = [
        {"text": "something unrelated", "score": 0.2, "metadata": {}},
    ]
    better_results = [
        {"text": "Eigenvalues satisfy Av=λv", "score": 0.8, "metadata": {}},
    ]

    call_count = {"n": 0}

    def mock_search(query, top_k=3):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return low_results
        return better_results

    with patch("rag.reflection.search", side_effect=mock_search):
        result = reflective_search("eigenvalues", top_k=1)

    assert result["attempts"] >= 2
    assert result["best_score"] >= 0.8
    print(f"✅ Retry test passed. Attempts: {result['attempts']}")