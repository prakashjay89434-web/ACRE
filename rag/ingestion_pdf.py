import arxiv
import pypdf
import os
import re
from rag.ingestion import add_texts


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    reader = pypdf.PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def ingest_pdf(pdf_path: str, metadata: dict = None) -> int:
    """Ingest a PDF file into Qdrant."""
    print(f"  [Ingestion] Reading PDF: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    print(f"  [Ingestion] Extracted {len(text)} characters")

    chunks = chunk_text(text)
    print(f"  [Ingestion] Split into {len(chunks)} chunks")

    metadatas = [metadata or {} for _ in chunks]
    add_texts(chunks, metadatas)
    print(f"  [Ingestion] Stored {len(chunks)} chunks in Qdrant")
    return len(chunks)


def ingest_arxiv(arxiv_id: str) -> int:
    """Download and ingest a paper from ArXiv."""
    import ssl
    import urllib.request

    print(f"  [Ingestion] Fetching ArXiv paper: {arxiv_id}")

    search = arxiv.Client().results(arxiv.Search(id_list=[arxiv_id]))
    paper = next(search)

    print(f"  [Ingestion] Title: {paper.title}")

    pdf_path = f"data/raw/{arxiv_id}.pdf"
    os.makedirs("data/raw", exist_ok=True)

    # Fix SSL on Windows
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    pdf_url = paper.pdf_url
    with urllib.request.urlopen(pdf_url, context=ssl_context) as response:
        with open(pdf_path, "wb") as f:
            f.write(response.read())

    print(f"  [Ingestion] Downloaded to {pdf_path}")

    metadata = {
        "title": paper.title,
        "authors": str(paper.authors[0]),
        "arxiv_id": arxiv_id,
        "source": "arxiv"
    }

    return ingest_pdf(pdf_path, metadata)


if __name__ == "__main__":
    # Test with a small ArXiv paper
    print("Testing ArXiv ingestion...")
    chunks = ingest_arxiv("2005.11401")  # RAG paper!
    print(f"✅ Ingested {chunks} chunks from RAG paper")