"""
Question-Answering pipeline module for DocuMind RAG.
Combines retrieval, prompt construction, LLM inference, anti-hallucination verification,
and citation structuring.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from rag.retriever import Retriever, get_retriever
from rag.prompt import SYSTEM_PROMPT, NO_ANSWER_FALLBACK, build_user_prompt

load_dotenv()
logger = logging.getLogger("documind.rag.qa")

DEFAULT_MODEL = "gpt-4o-mini"


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
        self.model_name = model_name or os.getenv("LLM_MODEL", os.getenv("OPENAI_MODEL", DEFAULT_MODEL))
        self.api_key = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", ""))
        self.base_url = os.getenv("LLM_BASE_URL", os.getenv("OPENAI_BASE_URL", None))

    def _call_llm(self, user_prompt: str) -> str:
        """
        Invokes LLM with system instructions and user prompt.
        Supports OpenAI SDK or OpenAI-compatible endpoint.
        """
        if not self.api_key:
            logger.warning("No LLM_API_KEY or OPENAI_API_KEY configured.")
            return ""

        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url if self.base_url else None
            )
            
            logger.info(f"Sending LLM request [model: {self.model_name}]...")
            response = client.chat.completions.create(
                model=self.model_name,
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

    def _extractive_fallback_check(self, question: str, chunks: List[Dict[str, Any]]) -> Optional[str]:
        """
        Fallback keyword/token alignment verification when running in offline/test mode
        without an active LLM API key.
        """
        if not chunks:
            return None

        # Simple semantic overlap check between question tokens and chunk content
        import re
        q_words = set(re.findall(r'\w+', question.lower()))
        # Remove common stopwords
        stopwords = {"what", "is", "the", "are", "of", "in", "and", "a", "an", "to", "for", "with", "on", "how", "why", "can", "does", "do", "about"}
        keywords = q_words - stopwords

        if not keywords:
            return None

        # Check if keywords appear across chunks
        found_in_chunks = False
        best_sentence = ""
        for chunk in chunks:
            text = chunk.get("text", "")
            lower_text = text.lower()
            matches = sum(1 for kw in keywords if kw in lower_text)
            if matches >= max(1, len(keywords) // 2):
                found_in_chunks = True
                # Pick a relevant matching sentence
                sentences = re.split(r'(?<=[.!?])\s+', text)
                for s in sentences:
                    if any(kw in s.lower() for kw in keywords):
                        best_sentence = s.strip()
                        break
                if best_sentence:
                    break

        if found_in_chunks and best_sentence:
            return best_sentence
        elif not found_in_chunks:
            return NO_ANSWER_FALLBACK
        return None

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
        4. Constructs grounded prompt and queries LLM.
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

        # 1. Retrieve relevant chunks
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

        # 2. Format grounded user prompt
        user_prompt = build_user_prompt(clean_question, chunks)

        # 3. Call LLM (or fallback if API key not present)
        answer = ""
        if self.api_key:
            try:
                answer = self._call_llm(user_prompt)
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                answer = f"Error communicating with LLM service: {e}"
        else:
            # Offline / local fallback when testing without API key
            logger.info("Running offline fallback logic (no API key configured).")
            fallback_ans = self._extractive_fallback_check(clean_question, chunks)
            if fallback_ans:
                answer = fallback_ans
            else:
                answer = NO_ANSWER_FALLBACK

        # 4. Check for anti-hallucination fallback in LLM answer
        is_fallback = (
            NO_ANSWER_FALLBACK.lower() in answer.lower()
            or "could not be found in the uploaded document" in answer.lower()
            or "not found in the document" in answer.lower()
            or "cannot find" in answer.lower() and "document" in answer.lower()
        )

        # 5. Format sources from retrieved chunks
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
            "answer": answer if answer else NO_ANSWER_FALLBACK,
            "sources": sources
        }


_qa_pipeline_instance: Optional[QAPipeline] = None


def get_qa_pipeline() -> QAPipeline:
    """Provides a singleton instance of QAPipeline."""
    global _qa_pipeline_instance
    if _qa_pipeline_instance is None:
        _qa_pipeline_instance = QAPipeline()
    return _qa_pipeline_instance
