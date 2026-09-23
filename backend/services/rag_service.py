"""
RAG (Retrieval-Augmented Generation) Service for DocuMind.
Coordinates document ingestion (chunking, embedding, vector storage)
and question-answering with citation extraction.
"""

import logging
from typing import Optional, List, Dict, Any

from models.schemas import QuestionResponse, Source, ExtractedDocument
from rag.chunker import chunk_document
from rag.embeddings import get_embedding_service
from rag.vector_store import get_vector_store
from rag.qa import get_qa_pipeline

logger = logging.getLogger("documind.services.rag")


def ingest_document(extracted_doc: ExtractedDocument) -> int:
    """
    Ingests an extracted document into the RAG vector pipeline:
    1. Splits extracted text into boundary-aware overlapping chunks.
    2. Generates dense embeddings using the sentence-transformers model.
    3. Persists chunks and embeddings in ChromaDB with document isolation metadata.

    Args:
        extracted_doc: ExtractedDocument instance containing text, filename, and page information.

    Returns:
        The total number of chunks stored in ChromaDB.
    """
    filename = extracted_doc.filename
    logger.info(f"Starting ingestion pipeline for document: '{filename}' ({extracted_doc.pages} pages)...")

    # 1. Chunk document
    chunks = chunk_document(
        filename=filename,
        text=extracted_doc.text,
        pages_data=extracted_doc.pages_data
    )
    logger.info(f"Document '{filename}' split into {len(chunks)} chunks.")

    if not chunks:
        logger.warning(f"No chunks generated for document '{filename}'.")
        return 0

    # 2. Generate embeddings
    embedding_service = get_embedding_service()
    chunk_texts = [c.text for c in chunks]
    embeddings = embedding_service.embed_texts(chunk_texts)
    logger.info(f"Generated {len(embeddings)} embeddings for '{filename}'.")

    # 3. Store in ChromaDB
    vector_store = get_vector_store()
    stored_count = vector_store.add_chunks(chunks=chunks, embeddings=embeddings, delete_existing=True)
    logger.info(f"Ingestion complete: {stored_count} chunks persisted to ChromaDB for '{filename}'.")

    return stored_count


def answer_question(
    question: str,
    filename: Optional[str] = None,
    top_k: Optional[int] = None
) -> QuestionResponse:
    """
    Processes a user question against the document vector store and returns a grounded answer with citations.

    Args:
        question: User query string.
        filename: Optional document filename to isolate search.
        top_k: Optional number of chunks to retrieve.

    Returns:
        QuestionResponse containing the grounded answer and supporting source citations.
    """
    logger.info(f"Processing Q&A query: '{question}' (filename filter: {filename})")
    qa_pipeline = get_qa_pipeline()
    result = qa_pipeline.answer_question(
        question=question,
        filename=filename,
        top_k=top_k
    )

    sources = [
        Source(
            filename=s.get("filename"),
            page=s.get("page"),
            text=s.get("text", "")
        )
        for s in result.get("sources", [])
    ]

    return QuestionResponse(
        answer=result.get("answer", ""),
        sources=sources
    )
