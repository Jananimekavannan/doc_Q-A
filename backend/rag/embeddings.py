"""
Embedding service for DocuMind RAG.
Loads lightweight sentence-transformer model ('all-MiniLM-L6-v2') once
and generates embeddings for document chunks and user questions.
"""

import os
import logging
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("documind.rag.embeddings")

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingService:
    """
    Singleton-capable embedding service using SentenceTransformer.
    """
    _instance: Optional["EmbeddingService"] = None

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", DEFAULT_MODEL_NAME)
        self._model = None
        self._load_model()

    def _load_model(self):
        """Loads the sentence transformer model into memory."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model '{self.model_name}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model '{self.model_name}': {e}")
            raise RuntimeError(f"Could not initialize embedding model '{self.model_name}': {e}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generates vector embeddings for a list of document chunk texts.

        Args:
            texts: List of text strings.

        Returns:
            List of embedding vectors (list of floats).
        """
        if not texts:
            return []

        if self._model is None:
            self._load_model()

        embeddings = self._model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Generates a vector embedding for a single user question query.

        Args:
            query: The user question string.

        Returns:
            Embedding vector (list of floats).
        """
        if not query or not query.strip():
            return []

        if self._model is None:
            self._load_model()

        embedding = self._model.encode(
            query.strip(),
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding.tolist()


_embedding_service_instance: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Provides a singleton instance of the EmbeddingService.
    Ensures the model is loaded into memory only once.
    """
    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService()
    return _embedding_service_instance
