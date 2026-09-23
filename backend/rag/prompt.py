"""
Prompt engineering and template module for DocuMind RAG.
Constructs strict grounded prompts ensuring answers use ONLY retrieved context
and strictly prevents hallucinations or invented answers.
"""

from typing import List, Dict, Any

SYSTEM_PROMPT = """You are a document question-answering assistant.

Answer the user's question using ONLY the provided document context.
Do not use outside knowledge.
Do not invent information.
If the answer cannot be found in the provided context, say that the answer could not be found in the uploaded document."""

NO_ANSWER_FALLBACK = "I couldn't find the answer in the uploaded document."


def format_context_blocks(retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Formats retrieved chunks into clear, cited context blocks for LLM consumption.

    Args:
        retrieved_chunks: List of retrieved chunk dictionaries.

    Returns:
        Formatted context string.
    """
    if not retrieved_chunks:
        return "No relevant context found."

    context_segments = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        meta = chunk.get("metadata", {})
        filename = meta.get("filename", "Document")
        page = meta.get("page")
        page_info = f", Page {page}" if page is not None else ""
        text = chunk.get("text", "").strip()

        segment = f"--- Context Passage {i} [Source: {filename}{page_info}] ---\n{text}"
        context_segments.append(segment)

    return "\n\n".join(context_segments)


def build_user_prompt(question: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Constructs the grounded user prompt containing ONLY retrieved chunks and the question.

    Args:
        question: User query.
        retrieved_chunks: List of retrieved chunk dictionaries.

    Returns:
        Assembled user prompt string.
    """
    context_text = format_context_blocks(retrieved_chunks)

    prompt = f"""DOCUMENT CONTEXT:
{context_text}

USER QUESTION:
{question}

INSTRUCTIONS:
Answer the question above based ONLY on the provided DOCUMENT CONTEXT. If the context does not contain enough information to answer truthfully, state: "{NO_ANSWER_FALLBACK}"."""

    return prompt
