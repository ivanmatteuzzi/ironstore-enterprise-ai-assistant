
import hashlib
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from src.ingestion import load_documents, split_documents


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORAGE_DIR = PROJECT_ROOT / "storage"
CHROMA_DIR = STORAGE_DIR / "chroma_db"

COLLECTION_NAME = "ironstore_knowledge"
EMBEDDING_MODEL = "text-embedding-3-small"


def create_chunk_ids(chunks):
    """Create stable IDs to avoid duplicate records on repeated runs."""
    ids = []

    for chunk in chunks:
        content = (
            f"{chunk.metadata['source']}|"
            f"{chunk.metadata['page']}|"
            f"{chunk.metadata.get('start_index', 0)}|"
            f"{chunk.page_content}"
        )

        chunk_id = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

        ids.append(chunk_id)

    return ids


def build_vector_store():
    load_dotenv(PROJECT_ROOT / ".env")

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY not found. Check the .env file."
        )

    print("\nSTEP 1: Loading documents...")
    pages = load_documents()

    print("\nSTEP 2: Splitting documents into chunks...")
    chunks = split_documents(pages)

    if not chunks:
        raise RuntimeError("No chunks available for embedding.")

    print(f"\nChunks to embed: {len(chunks)}")

    print("\nSTEP 3: Initializing embeddings...")
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    print("\nSTEP 4: Creating Chroma vector store...")
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        ids=create_chunk_ids(chunks),
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )

    print(f"Actual records in Chroma: {vector_store._collection.count()}")
    print("\nVECTOR STORE CREATED")
    print(f"Stored chunks: {len(chunks)}")
    print(f"Database location: {CHROMA_DIR}")

    return vector_store


def test_retrieval(vector_store):
    query = (
        "How should customer support escalate "
        "an unresolved customer issue?"
    )

    print("\nSTEP 5: Testing semantic retrieval...")
    results = vector_store.similarity_search(
        query,
        k=3
    )

    for index, doc in enumerate(results, start=1):
        print(f"\nRESULT {index}")
        print(f"Document: {doc.metadata['filename']}")
        print(f"Page: {doc.metadata['page']}")
        print(f"Department: {doc.metadata['department']}")
        print(f"Content: {doc.page_content[:350]}")


def main():
    vector_store = build_vector_store()
    test_retrieval(vector_store)


if __name__ == "__main__":
    main()
