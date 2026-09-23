"""
Retriever module for DocuMind RAG.
Coordinates embedding generation for user queries and similarity retrieval
from ChromaDB with configurable top_k and metadata filtering.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from rag.embeddings import EmbeddingService, get_embedding_service
from rag.vector_store import VectorStoreService, get_vector_store

load_dotenv()
logger = logging.getLogger("documind.rag.retriever")

DEFAULT_TOP_K = 3


class Retriever:
    """
    Retrieves the most relevant document chunks for a given user query.
    """
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store: Optional[VectorStoreService] = None,
        top_k: Optional[int] = None
    ):
        self.embedding_service = embedding_service or get_embedding_service()
        self.vector_store = vector_store or get_vector_store()
        env_top_k = os.getenv("TOP_K")
        self.top_k = int(env_top_k) if env_top_k and env_top_k.isdigit() else (top_k or DEFAULT_TOP_K)

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filename: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_k most relevant chunks for the question.

        Args:
            query: The user question.
            top_k: Optional override for the number of chunks to retrieve.
            filename: Optional filename filter for document isolation.

        Returns:
            List of chunk dicts: [{'text': '...', 'metadata': {'filename': ..., 'page': ..., 'chunk_index': ...}}]
        """
        if not query or not query.strip():
            return []

        k = top_k or self.top_k
        logger.info(f"Retrieving top {k} chunks for query: '{query[:50]}...' [filter filename: {filename}]")

        # 1. Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)
        if not query_embedding:
            return []

        # 2. Similarity search in ChromaDB
        results = self.vector_store.query_similar(
            query_embedding=query_embedding,
            top_k=k,
            filename=filename
        )

        logger.info(f"Retrieved {len(results)} chunks from vector store.")
        return results


_retriever_instance: Optional[Retriever] = None


def get_retriever() -> Retriever:
    """
    Provides a singleton or reusable instance of the Retriever.
    """
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = Retriever()
    return _retriever_instance
