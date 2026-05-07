from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid


COLLECTION_NAME = "acre_knowledge"
EMBEDDING_SIZE = 384
MODEL_NAME = "BAAI/bge-small-en-v1.5"


def get_client() -> QdrantClient:
    """Local persistent Qdrant client."""
    return QdrantClient(path="data/vectors")


def get_embedder() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def create_collection(client: QdrantClient):
    """Create collection if it doesn't exist."""
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"Created collection: {COLLECTION_NAME}")
    else:
        print(f"Collection already exists: {COLLECTION_NAME}")


def add_texts(texts: list[str], metadatas: list[dict] = None):
    """Embed and store texts in Qdrant."""
    client = get_client()
    embedder = get_embedder()
    create_collection(client)

    if metadatas is None:
        metadatas = [{} for _ in texts]

    vectors = embedder.encode(texts, show_progress_bar=False).tolist()

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vectors[i],
            payload={"text": texts[i], **metadatas[i]}
        )
        for i in range(len(texts))
    ]

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Added {len(texts)} texts to Qdrant")


def search(query: str, top_k: int = 3) -> list[dict]:
    """Search for relevant chunks."""
    client = get_client()
    embedder = get_embedder()

    query_vector = embedder.encode([query])[0].tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    ).points

    return [
        {
            "text": r.payload.get("text", ""),
            "score": r.score,
            "metadata": {k: v for k, v in r.payload.items() if k != "text"}
        }
        for r in results
    ]