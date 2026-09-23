"""
Tests for DocuMind RAG components:
- Chunker
- Embeddings
- Vector Store (ChromaDB)
- Retriever
- Prompt Builder
- QA Pipeline & Hallucination Prevention
"""

import sys
from pathlib import Path
import pytest

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from rag.chunker import chunk_document, split_text_with_overlap, DocumentChunk
from rag.prompt import build_user_prompt, format_context_blocks, SYSTEM_PROMPT, NO_ANSWER_FALLBACK
from rag.vector_store import VectorStoreService
from rag.retriever import Retriever
from rag.qa import QAPipeline


# 1. Test Chunking
def test_chunker_basic_split():
    text = "Short text."
    chunks = split_text_with_overlap(text, chunk_size=100, overlap=20)
    assert len(chunks) == 1
    assert chunks[0] == "Short text."


def test_chunker_long_text_overlap():
    long_text = " ".join([f"Sentence number {i} with some descriptive content." for i in range(50)])
    chunks = split_text_with_overlap(long_text, chunk_size=300, overlap=50)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 350  # Boundary margin


def test_chunker_document_with_pages():
    pages_data = [
        {"page": 1, "text": "Page 1 intro to machine learning and neural networks."},
        {"page": 2, "text": "Page 2 discussion on gradient descent and optimization algorithms."}
    ]
    chunks = chunk_document(
        filename="test_guide.pdf",
        text="Full text combined...",
        pages_data=pages_data,
        chunk_size=500,
        overlap=50
    )
    assert len(chunks) >= 2
    assert chunks[0].metadata["filename"] == "test_guide.pdf"
    assert chunks[0].metadata["page"] == 1
    assert chunks[1].metadata["page"] == 2
    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[1].metadata["chunk_index"] == 1


# 2. Test Prompt Construction
def test_prompt_formatting():
    chunks = [
        {
            "text": "Supervised learning uses labeled training data.",
            "metadata": {"filename": "ai_notes.pdf", "page": 3, "chunk_index": 0}
        },
        {
            "text": "Unsupervised learning finds hidden patterns in unlabeled data.",
            "metadata": {"filename": "ai_notes.pdf", "page": 4, "chunk_index": 1}
        }
    ]
    formatted = format_context_blocks(chunks)
    assert "ai_notes.pdf" in formatted
    assert "Page 3" in formatted
    assert "Page 4" in formatted
    assert "Supervised learning" in formatted

    prompt = build_user_prompt("What is supervised learning?", chunks)
    assert "DOCUMENT CONTEXT:" in prompt
    assert "USER QUESTION:" in prompt
    assert "What is supervised learning?" in prompt
    assert NO_ANSWER_FALLBACK in prompt


# 3. Test Vector Store & Similarity Search with Temp Directory
def test_vector_store_operations(tmp_path):
    vs = VectorStoreService(persist_directory=str(tmp_path / "test_chroma"), collection_name="test_col")
    
    # 2 dummy chunks with 4-dim dummy embeddings
    c1 = DocumentChunk(
        text="DocuMind is an AI document Q&A assistant.",
        metadata={"filename": "doc1.txt", "page": 1, "chunk_index": 0}
    )
    c2 = DocumentChunk(
        text="PostgreSQL is a relational database management system.",
        metadata={"filename": "doc2.txt", "page": 1, "chunk_index": 0}
    )

    vs.add_chunks(
        chunks=[c1, c2],
        embeddings=[[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]],
        delete_existing=True
    )

    assert vs.get_total_count() == 2

    # Query nearest to c1
    results = vs.query_similar(query_embedding=[0.9, 0.1, 0.0, 0.0], top_k=1)
    assert len(results) == 1
    assert "DocuMind" in results[0]["text"]
    assert results[0]["metadata"]["filename"] == "doc1.txt"

    # Test Document Isolation / Filtering
    results_filtered = vs.query_similar(
        query_embedding=[0.9, 0.1, 0.0, 0.0],
        top_k=5,
        filename="doc2.txt"
    )
    assert len(results_filtered) == 1
    assert results_filtered[0]["metadata"]["filename"] == "doc2.txt"


# 4. Test QA Pipeline In-Document vs Out-of-Document (Hallucination Prevention)
def test_qa_pipeline_hallucination_fallback(tmp_path):
    vs = VectorStoreService(persist_directory=str(tmp_path / "test_qa_chroma"), collection_name="test_qa_col")
    
    chunk = DocumentChunk(
        text="The solar system consists of the Sun and eight planets orbiting around it.",
        metadata={"filename": "astronomy.txt", "page": 1, "chunk_index": 0}
    )
    # 3-dim vector
    vs.add_chunks(chunks=[chunk], embeddings=[[1.0, 0.0, 0.0]])

    class MockEmbeddingService:
        def embed_query(self, q):
            return [1.0, 0.0, 0.0]

    retriever = Retriever(
        embedding_service=MockEmbeddingService(),
        vector_store=vs,
        top_k=1
    )

    qa = QAPipeline(retriever=retriever)

    # In-context query
    res_in = qa.answer_question("What does the solar system consist of?")
    assert "solar system" in res_in["answer"].lower()
    assert len(res_in["sources"]) > 0
    assert res_in["sources"][0]["filename"] == "astronomy.txt"

    # Out-of-context query
    res_out = qa.answer_question("What is the population of Tokyo?")
    assert res_out["answer"] == NO_ANSWER_FALLBACK
    assert res_out["sources"] == []
