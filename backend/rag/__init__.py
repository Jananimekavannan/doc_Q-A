"""
DocuMind RAG (Retrieval-Augmented Generation) package.
Modular components for document chunking, embeddings, ChromaDB vector storage,
semantic retrieval, grounded prompt construction, and question-answering.
"""

from rag.chunker import DocumentChunk, chunk_document, split_text_with_overlap
from rag.embeddings import EmbeddingService, get_embedding_service
from rag.vector_store import VectorStoreService, get_vector_store
from rag.retriever import Retriever, get_retriever
from rag.prompt import SYSTEM_PROMPT, NO_ANSWER_FALLBACK, build_user_prompt, format_context_blocks
from rag.qa import QAPipeline, get_qa_pipeline

__all__ = [
    "DocumentChunk",
    "chunk_document",
    "split_text_with_overlap",
    "EmbeddingService",
    "get_embedding_service",
    "VectorStoreService",
    "get_vector_store",
    "Retriever",
    "get_retriever",
    "SYSTEM_PROMPT",
    "NO_ANSWER_FALLBACK",
    "build_user_prompt",
    "format_context_blocks",
    "QAPipeline",
    "get_qa_pipeline",
]
