"""
ChromaDB Vector Store Manager for Knowledge Assistant.
"""

from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions

# 1. Initialize persistent storage directory for ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# 2. Setup embedding function using local Sentence Transformers model
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# 3. Create or fetch the document collection
collection = chroma_client.get_or_create_collection(
    name="knowledge_base",
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"}
)


def add_chunks_to_vectorstore(chunks: List[Dict[str, Any]]) -> int:
    """
    Stores document chunks into ChromaDB with automatically generated embeddings.
    """
    if not chunks:
        return 0

    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    return len(ids)


def query_vectorstore(query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
    """
    Queries ChromaDB for the top-K most semantically similar text chunks.
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )

    formatted_results = []
    if results and results.get("documents"):
        docs = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0] if "distances" in results and results["distances"] else [0] * len(docs)
        ids = results["ids"][0]

        for doc, meta, dist, chunk_id in zip(docs, metadatas, distances, ids):
            formatted_results.append({
                "chunk_id": chunk_id,
                "text": doc,
                "metadata": meta,
                "distance": round(dist, 4)
            })

    return formatted_results