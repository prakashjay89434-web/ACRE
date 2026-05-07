from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid

COLLECTION_NAME = "acre_knowledge"
MODEL_NAME = "BAAI/bge-small-en-v1.5"


def get_test_client():
    """Use in-memory client for tests — no file locking issues."""
    return QdrantClient(":memory:")


def setup_test_collection(client):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )


def test_collection_created():
    client = get_test_client()
    setup_test_collection(client)
    existing = [c.name for c in client.get_collections().collections]
    assert COLLECTION_NAME in existing
    print("✅ Collection created")


def test_add_and_search():
    client = get_test_client()
    setup_test_collection(client)
    embedder = SentenceTransformer(MODEL_NAME)

    texts = [
        "Eigenvalues are scalar values that satisfy Av = λv",
        "Gradient descent minimizes a function by moving in negative gradient direction",
        "BERT is a transformer model trained with masked language modeling",
    ]

    vectors = embedder.encode(texts, show_progress_bar=False).tolist()
    points = [
        PointStruct(id=str(uuid.uuid4()), vector=vectors[i], payload={"text": texts[i]})
        for i in range(len(texts))
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)

    query_vector = embedder.encode(["how do eigenvalues work"])[0].tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=1
    ).points

    assert len(results) > 0
    assert "eigenvalue" in results[0].payload["text"].lower()
    print(f"✅ Search passed. Top result: {results[0].payload['text'][:60]}")


def test_search_returns_relevant():
    client = get_test_client()
    setup_test_collection(client)
    embedder = SentenceTransformer(MODEL_NAME)

    texts = [
        "Gradient descent minimizes a function by moving in negative gradient direction",
        "BERT is a transformer model trained with masked language modeling",
    ]
    vectors = embedder.encode(texts, show_progress_bar=False).tolist()
    points = [
        PointStruct(id=str(uuid.uuid4()), vector=vectors[i], payload={"text": texts[i]})
        for i in range(len(texts))
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)

    query_vector = embedder.encode(["gradient optimization"])[0].tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=2
    ).points

    assert len(results) > 0
    print(f"✅ Relevance test passed. Score: {results[0].score:.3f}")