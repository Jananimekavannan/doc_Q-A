"""
RAG (Retrieval-Augmented Generation) Service for DocuMind.
Provides the interface for querying the knowledge base and generating answers with sources.

NOTE FOR AI/RAG TEAMMATE:
This module is the integration point for:
1. Embedding generation (e.g. OpenAI / HuggingFace embeddings)
2. Vector store querying (e.g. ChromaDB similarity search)
3. Prompt construction with retrieved context passages
4. LLM response generation (e.g. GPT-4o / Claude)
5. Source citation extraction

Currently returns a placeholder response for backend testing until RAG pipeline is connected.
"""

from typing import Optional
from models.schemas import QuestionResponse, Source


def answer_question(question: str) -> QuestionResponse:
    """
    Processes a user question against the document store and returns an answer with citations.

    Args:
        question: User query string.

    Returns:
        QuestionResponse containing the generated answer and supporting source passages.
    """
    # Placeholder response for backend foundation testing.
    # The AI/RAG teammate will connect chunk retrieval and LLM response generation here.
    return QuestionResponse(
        answer="RAG service not connected. Please connect embeddings and vector store to enable Q&A.",
        sources=[]
    )
