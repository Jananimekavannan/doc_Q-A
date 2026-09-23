"""
Document chunking module for DocuMind RAG.
Splits document text into overlapping chunks while preserving word/sentence
boundaries and document metadata (filename, page, chunk_index).
"""

import re
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any


@dataclass
class DocumentChunk:
    """
    Represents a single chunk of document text along with its metadata.
    """
    text: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "metadata": self.metadata
        }


def split_text_with_overlap(
    text: str,
    chunk_size: int = 900,
    overlap: int = 150
) -> List[str]:
    """
    Splits a single text string into overlapping chunks without breaking words mid-way.
    
    Args:
        text: The input text to split.
        chunk_size: Target maximum characters per chunk (approx 800-1000).
        overlap: Character overlap between consecutive chunks (approx 100-200).

    Returns:
        List of text chunks.
    """
    clean_text = text.strip()
    if not clean_text:
        return []

    if len(clean_text) <= chunk_size:
        return [clean_text]

    chunks: List[str] = []
    start = 0
    text_length = len(clean_text)

    while start < text_length:
        end = start + chunk_size

        if end >= text_length:
            chunk = clean_text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Look for natural split boundaries near the target end position
        # Preference: paragraph break > newline > sentence end > word space
        split_pos = -1
        search_window = clean_text[start:end]

        # Check for paragraph break (\n\n)
        p_break = search_window.rfind("\n\n")
        if p_break != -1 and p_break >= chunk_size // 2:
            split_pos = start + p_break + 2

        # Check for newline (\n)
        if split_pos == -1:
            nl_break = search_window.rfind("\n")
            if nl_break != -1 and nl_break >= chunk_size // 2:
                split_pos = start + nl_break + 1

        # Check for sentence endings (. / ? / !)
        if split_pos == -1:
            punct_matches = list(re.finditer(r'[.!?]\s', search_window))
            if punct_matches:
                last_punct = punct_matches[-1]
                if last_punct.end() >= chunk_size // 2:
                    split_pos = start + last_punct.end()

        # Check for space
        if split_pos == -1:
            space_pos = search_window.rfind(" ")
            if space_pos != -1 and space_pos >= chunk_size // 2:
                split_pos = start + space_pos + 1

        # If no clean boundary found in reasonable window, hard split at end
        if split_pos == -1 or split_pos <= start:
            split_pos = end

        chunk = clean_text[start:split_pos].strip()
        if chunk:
            chunks.append(chunk)

        # Advance start position with overlap
        start = max(start + 1, split_pos - overlap)

    return chunks


def chunk_document(
    filename: str,
    text: str,
    pages_data: Optional[List[Dict[str, Any]]] = None,
    chunk_size: int = 900,
    overlap: int = 150
) -> List[DocumentChunk]:
    """
    Chunks a full document into DocumentChunk objects with accurate metadata.

    Args:
        filename: Name of the uploaded document (e.g. 'sample.pdf').
        text: Complete extracted document text.
        pages_data: Optional list of per-page text entries: [{'page': 1, 'text': '...'}].
        chunk_size: Target chunk size in characters (approx 800-1000).
        overlap: Overlap size in characters (approx 100-200).

    Returns:
        List of DocumentChunk instances with preserved metadata.
    """
    chunks: List[DocumentChunk] = []
    chunk_index = 0

    if pages_data and len(pages_data) > 0:
        # Document with per-page structure (e.g., PDF)
        for page_info in pages_data:
            page_num = page_info.get("page")
            page_text = page_info.get("text", "").strip()
            if not page_text:
                continue

            raw_chunks = split_text_with_overlap(page_text, chunk_size=chunk_size, overlap=overlap)
            for raw_chunk in raw_chunks:
                metadata = {
                    "filename": filename,
                    "page": page_num,
                    "chunk_index": chunk_index
                }
                chunks.append(DocumentChunk(text=raw_chunk, metadata=metadata))
                chunk_index += 1
    else:
        # Flat document (e.g., TXT file or fallback)
        raw_chunks = split_text_with_overlap(text, chunk_size=chunk_size, overlap=overlap)
        for raw_chunk in raw_chunks:
            metadata = {
                "filename": filename,
                "page": 1,
                "chunk_index": chunk_index
            }
            chunks.append(DocumentChunk(text=raw_chunk, metadata=metadata))
            chunk_index += 1

    return chunks
