"""
Document Service for DocuMind.
Handles text extraction from PDF and TXT files.
Kept modular and independent from RAG / vector logic.
"""

import os
from pathlib import Path
from typing import Union
from pypdf import PdfReader

from models.schemas import ExtractedDocument


def extract_text_from_txt(file_path: Union[str, Path], filename: str = "") -> ExtractedDocument:
    """
    Safely extracts text content from a plain text (.txt) file using UTF-8 encoding,
    with graceful fallback for other encodings.

    Args:
        file_path: Path to the TXT file on disk.
        filename: Optional display name for the document.

    Returns:
        ExtractedDocument containing filename, page count (1 for txt), and text.
    """
    path = Path(file_path)
    doc_name = filename or path.name

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read bytes and try decoding as UTF-8 first, fallback to latin-1 / utf-8 with replacement
    raw_bytes = path.read_bytes()
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw_bytes.decode("utf-8", errors="replace")
        except Exception:
            text = raw_bytes.decode("latin-1", errors="replace")

    return ExtractedDocument(
        filename=doc_name,
        pages=1,
        text=text.strip(),
        pages_data=[{"page": 1, "text": text.strip()}]
    )


def extract_text_from_pdf(file_path: Union[str, Path], filename: str = "") -> ExtractedDocument:
    """
    Extracts text page-by-page from a PDF document using PyPDF.

    Args:
        file_path: Path to the PDF file on disk.
        filename: Optional display name for the document.

    Returns:
        ExtractedDocument containing filename, total page count, combined text, and per-page entries.
    """
    path = Path(file_path)
    doc_name = filename or path.name

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    reader = PdfReader(str(path))
    pages_count = len(reader.pages)
    page_texts = []
    pages_data = []

    for i, page in enumerate(reader.pages):
        page_num = i + 1
        page_text = (page.extract_text() or "").strip()
        if page_text:
            page_texts.append(page_text)
            pages_data.append({"page": page_num, "text": page_text})

    full_text = "\n\n".join(page_texts)

    return ExtractedDocument(
        filename=doc_name,
        pages=pages_count,
        text=full_text,
        pages_data=pages_data
    )


def extract_document_text(file_path: Union[str, Path], filename: str = "") -> ExtractedDocument:
    """
    Unified extraction dispatcher that detects file extension and extracts text.

    Args:
        file_path: Path to the document file.
        filename: Optional file name to determine type.

    Returns:
        ExtractedDocument containing metadata and full extracted text.
    """
    path = Path(file_path)
    target_name = filename or path.name
    ext = os.path.splitext(target_name)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path, target_name)
    elif ext == ".txt":
        return extract_text_from_txt(file_path, target_name)
    else:
        raise ValueError(f"Unsupported file extension: {ext}. Only .pdf and .txt are supported.")
