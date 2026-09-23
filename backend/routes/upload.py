"""
Upload router for DocuMind.
Handles document upload (PDF/TXT), validation, storage in backend/uploads, and extraction.
"""

import os
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from dotenv import load_dotenv

from models.schemas import DocumentResponse, ErrorResponse
from services.document_service import extract_document_text

load_dotenv()

router = APIRouter(tags=["Document Operations"])

MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

BASE_BACKEND_DIR = Path(__file__).resolve().parent.parent
env_upload_dir = os.getenv("UPLOAD_DIR", "uploads")
UPLOAD_DIR = (BASE_BACKEND_DIR / env_upload_dir).resolve() if not os.path.isabs(env_upload_dir) else Path(env_upload_dir)


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload a PDF or TXT document",
    description="Accepts multipart/form-data with a file field (PDF or TXT, max 20 MB).",
    responses={
        200: {"model": DocumentResponse, "description": "Document uploaded successfully"},
        400: {"model": ErrorResponse, "description": "Unsupported file type or invalid format"},
        413: {"model": ErrorResponse, "description": "File size exceeds maximum allowed size"},
        500: {"model": ErrorResponse, "description": "Internal server processing error"},
    },
)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and validate a document file (PDF or TXT).
    Saves file to backend/uploads/ and verifies text extraction.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file was uploaded or file name is empty."
        )

    # Sanitize filename (take only base name to prevent directory traversal)
    original_filename = Path(file.filename).name
    if not original_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename."
        )

    ext = Path(original_filename).suffix.lower()

    if ext not in [".pdf", ".txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT files are supported."
        )

    file_type = "pdf" if ext == ".pdf" else "txt"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination_path = UPLOAD_DIR / original_filename

    total_size = 0
    chunk_size = 1024 * 1024  # 1 MB chunk buffer

    try:
        with open(destination_path, "wb") as buffer:
            while chunk := await file.read(chunk_size):
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE_BYTES:
                    buffer.close()
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE if hasattr(status, "HTTP_413_CONTENT_TOO_LARGE") else 413,
                        detail=f"File size exceeds the {MAX_FILE_SIZE_MB} MB limit."
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception:
        if destination_path.exists():
            destination_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while saving the file."
        )
    finally:
        await file.close()

    # Validate that document content can be extracted cleanly
    try:
        extract_document_text(destination_path, original_filename)
    except Exception as e:
        if destination_path.exists():
            destination_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read document contents: {str(e)}"
        )

    return DocumentResponse(
        message="Document uploaded successfully",
        filename=original_filename,
        file_type=file_type,
        size=total_size
    )
