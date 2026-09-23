"""
Vector Store module for DocuMind RAG using ChromaDB.
Manages persistent local vector storage, document embedding insertion,
document isolation filtering, and similarity search.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from rag.chunker import DocumentChunk

load_dotenv()
logger = logging.getLogger("documind.rag.vector_store")

DEFAULT_PERSIST_DIRECTORY = "./chroma_db"
DEFAULT_COLLECTION_NAME = "documind_collection"


class VectorStoreService:
    """
    Manages interactions with local persistent ChromaDB vector database.
    """
    _instance: Optional["VectorStoreService"] = None

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = DEFAULT_COLLECTION_NAME
    ):
        raw_persist_dir = persist_directory or os.getenv("CHROMA_PERSIST_DIRECTORY", DEFAULT_PERSIST_DIRECTORY)
        # Resolve relative path with respect to backend directory
        backend_dir = Path(__file__).resolve().parent.parent
        self.persist_directory = str((backend_dir / raw_persist_dir).resolve() if not os.path.isabs(raw_persist_dir) else Path(raw_persist_dir))
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        self._init_db()

    def _init_db(self):
        """Initializes ChromaDB persistent client and collection."""
        try:
            import chromadb
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.persist_directory)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"ChromaDB initialized at '{self.persist_directory}' [collection: {self.collection_name}].")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise RuntimeError(f"Could not initialize ChromaDB vector store: {e}")

    def add_chunks(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
        delete_existing: bool = True
    ) -> int:
        """
        Stores document chunks and their embeddings into ChromaDB.
        Optionally deletes existing chunks for the same filename to avoid duplication on re-upload.

        Args:
            chunks: List of DocumentChunk instances.
            embeddings: List of embedding vectors matching chunks.
            delete_existing: If True, purges older entries for the document first.

        Returns:
            Number of chunks successfully indexed.
        """
        if not chunks:
            return 0

        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings.")

        filename = chunks[0].metadata.get("filename")
        if delete_existing and filename:
            self.delete_document(filename)

        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_filename = chunk.metadata.get("filename", "unknown_doc")
            chunk_page = chunk.metadata.get("page", 1)
            chunk_idx = chunk.metadata.get("chunk_index", i)

            chunk_id = f"{chunk_filename}_p{chunk_page}_c{chunk_idx}"
            ids.append(chunk_id)
            documents.append(chunk.text)
            
            # ChromaDB metadata values must be str, int, float, or bool
            metadatas.append({
                "filename": str(chunk_filename),
                "page": int(chunk_page) if chunk_page is not None else 1,
                "chunk_index": int(chunk_idx)
            })

        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        logger.info(f"Stored {len(chunks)} chunks for '{filename}' in ChromaDB.")
        return len(chunks)

    def delete_document(self, filename: str):
        """
        Deletes all chunks belonging to a specific filename for document lifecycle management.
        """
        try:
            # Query if document exists
            existing = self._collection.get(where={"filename": filename})
            if existing and existing.get("ids"):
                self._collection.delete(where={"filename": filename})
                logger.info(f"Purged previous entries for document '{filename}' from ChromaDB.")
        except Exception as e:
            logger.warning(f"Notice during document purge for '{filename}': {e}")

    def query_similar(
        self,
        query_embedding: List[float],
        top_k: int = 3,
        filename: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs similarity search in ChromaDB.

        Args:
            query_embedding: Query embedding vector.
            top_k: Number of nearest chunks to retrieve.
            filename: Optional filename filter for document isolation.

        Returns:
            List of dicts: [{'text': '...', 'metadata': {...}, 'distance': 0.12, 'id': '...'}]
        """
        if not query_embedding:
            return []

        # Check if collection is empty
        count = self._collection.count()
        if count == 0:
            logger.info("ChromaDB collection is empty.")
            return []

        query_params: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, count),
            "include": ["documents", "metadatas", "distances"]
        }

        if filename:
            query_params["where"] = {"filename": filename}

        try:
            results = self._collection.query(**query_params)
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []

        retrieved = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            ids = results["ids"][0] if "ids" in results else [""] * len(docs)

            for doc_text, meta, dist, cid in zip(docs, metas, distances, ids):
                retrieved.append({
                    "id": cid,
                    "text": doc_text,
                    "metadata": meta,
                    "distance": dist
                })

        return retrieved

    def get_total_count(self) -> int:
        """Returns the total number of chunks stored."""
        return self._collection.count() if self._collection else 0


_vector_store_instance: Optional[VectorStoreService] = None


def get_vector_store() -> VectorStoreService:
    """
    Provides a singleton instance of the VectorStoreService.
    """
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStoreService()
    return _vector_store_instance
