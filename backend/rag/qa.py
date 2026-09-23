"""
Question-Answering pipeline module for DocuMind RAG.
Combines retrieval, prompt construction, LLM inference, semantic ranking,
anti-hallucination verification, and citation structuring.
"""

import os
import re
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from rag.retriever import Retriever, get_retriever
from rag.prompt import SYSTEM_PROMPT, NO_ANSWER_FALLBACK, build_user_prompt

load_dotenv()
logger = logging.getLogger("documind.rag.qa")

DEFAULT_MODEL = "gpt-4o-mini"
SEMANTIC_RELEVANCE_THRESHOLD = 0.25


class QAPipeline:
    """
    Executes the full RAG Q&A workflow.
    """
    def __init__(
        self,
        retriever: Optional[Retriever] = None,
        model_name: Optional[str] = None
    ):
        self.retriever = retriever or get_retriever()
        self._model_name = model_name

    def _get_api_config(self):
        """Reads LLM configuration dynamically from environment."""
        load_dotenv()
        api_key = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", "")).strip()
        model_name = self._model_name or os.getenv("LLM_MODEL", os.getenv("OPENAI_MODEL", DEFAULT_MODEL)).strip()
        base_url = os.getenv("LLM_BASE_URL", os.getenv("OPENAI_BASE_URL", None))
        if base_url:
            base_url = base_url.strip()
        return api_key, model_name, base_url

    def _call_llm(self, user_prompt: str, api_key: str, model_name: str, base_url: Optional[str]) -> str:
        """
        Invokes LLM with system instructions and user prompt.
        Supports OpenAI SDK or OpenAI-compatible endpoint.
        """
        if not api_key:
            return ""

        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=api_key,
                base_url=base_url if base_url else None
            )
            
            logger.info(f"Sending LLM request [model: {model_name}]...")
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=500
            )
            raw_answer = response.choices[0].message.content
            logger.info("LLM response generated successfully.")
            return raw_answer.strip() if raw_answer else ""
        except Exception as e:
            logger.error(f"Error during LLM call: {e}")
            raise RuntimeError(f"LLM generation failed: {e}")

    def _extract_grounded_answer(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Synthesizes a grounded answer from retrieved chunks using semantic sentence embeddings
        when running in local/offline mode without an active LLM API key.
        """
        if not chunks:
            return NO_ANSWER_FALLBACK

        # 1. Extract all sentences from retrieved chunks
        sentences: List[str] = []
        for chunk in chunks:
            text = chunk.get("text", "").strip()
            if not text:
                continue
            split_items = [
                s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', text)
                if s.strip()
            ]
            for item in split_items:
                if len(item) >= 3:
                    sentences.append(item)
            if not split_items and text:
                sentences.append(text)

        if not sentences:
            return NO_ANSWER_FALLBACK

        # 2. Embed sentences and query using sentence-transformers
        embedding_service = self.retriever.embedding_service
        q_emb = np.array(embedding_service.embed_query(question), dtype=np.float32)
        s_embs = np.array(embedding_service.embed_texts(sentences), dtype=np.float32)

        # 3. Compute cosine similarities
        q_norm = np.linalg.norm(q_emb) + 1e-9
        s_norms = np.linalg.norm(s_embs, axis=1) + 1e-9
        similarities = np.dot(s_embs, q_emb) / (s_norms * q_norm)

        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])
        logger.info(f"Offline semantic ranking: best sentence score = {best_score:.4f}")

        # Check against anti-hallucination threshold
        if best_score < SEMANTIC_RELEVANCE_THRESHOLD:
            logger.info(f"Query '{question}' score ({best_score:.4f}) is below threshold ({SEMANTIC_RELEVANCE_THRESHOLD}).")
            return NO_ANSWER_FALLBACK

        # 4. Pick top relevant sentences (preserving original document flow)
        score_cutoff = max(SEMANTIC_RELEVANCE_THRESHOLD, best_score * 0.70)
        selected_indices = [
            i for i, score in enumerate(similarities)
            if score >= score_cutoff
        ]
        # Keep up to 3 most relevant sentences in document order
        selected_indices = sorted(selected_indices, key=lambda i: similarities[i], reverse=True)[:3]
        selected_indices.sort()

        selected_sentences = [sentences[i] for i in selected_indices]
        return " ".join(selected_sentences)

    def answer_question(
        self,
        question: str,
        filename: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes question answering:
        1. Embeds question and retrieves top_k chunks from vector store.
        2. If vector store is empty -> returns no documents message.
        3. If no chunks retrieved -> returns NO_ANSWER_FALLBACK.
        4. Constructs grounded prompt and queries LLM (or uses semantic extractor).
        5. Formats answer and returns supporting source passages.

        Args:
            question: User query string.
            filename: Optional document filename for isolated search.
            top_k: Optional number of chunks to retrieve.

        Returns:
            Dict containing 'answer' and 'sources' list.
        """
        clean_question = question.strip()
        if not clean_question:
            return {
                "answer": "Please ask a valid question.",
                "sources": []
            }

        # Check vector store chunk count
        total_stored = self.retriever.vector_store.get_total_count()
        if total_stored == 0:
            return {
                "answer": "No documents have been uploaded yet. Please upload a PDF or TXT document first.",
                "sources": []
            }

        # 1. Retrieve relevant chunks from ChromaDB
        chunks = self.retriever.retrieve(
            query=clean_question,
            top_k=top_k,
            filename=filename
        )

        if not chunks:
            logger.info("No relevant chunks retrieved from vector store.")
            return {
                "answer": NO_ANSWER_FALLBACK,
                "sources": []
            }

        api_key, model_name, base_url = self._get_api_config()

        # 2. Call LLM if API key is provided, otherwise use semantic extractor
        answer = ""
        if api_key:
            try:
                user_prompt = build_user_prompt(clean_question, chunks)
                answer = self._call_llm(user_prompt, api_key, model_name, base_url)
            except Exception as e:
                logger.error(f"LLM call failed: {e}. Falling back to semantic extraction.")
                answer = self._extract_grounded_answer(clean_question, chunks)
        else:
            logger.info("No LLM API key detected; running semantic extraction.")
            answer = self._extract_grounded_answer(clean_question, chunks)

        # 3. Check for anti-hallucination fallback in answer
        is_fallback = (
            not answer
            or NO_ANSWER_FALLBACK.lower() in answer.lower()
            or "could not be found in the uploaded document" in answer.lower()
            or "not found in the document" in answer.lower()
            or ("cannot find" in answer.lower() and "document" in answer.lower())
        )

        # 4. Format sources from retrieved chunks
        sources = []
        if not is_fallback:
            for chunk in chunks:
                meta = chunk.get("metadata", {})
                source_item = {
                    "filename": meta.get("filename", "document"),
                    "page": meta.get("page", 1),
                    "text": chunk.get("text", "")
                }
                sources.append(source_item)

        return {
            "answer": answer if answer and not is_fallback else NO_ANSWER_FALLBACK,
            "sources": sources
        }


_qa_pipeline_instance: Optional[QAPipeline] = None


def get_qa_pipeline() -> QAPipeline:
    """Provides a singleton instance of QAPipeline."""
    global _qa_pipeline_instance
    if _qa_pipeline_instance is None:
        _qa_pipeline_instance = QAPipeline()
    return _qa_pipeline_instance
