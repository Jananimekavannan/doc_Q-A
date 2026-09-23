"""
Pydantic Schemas for DocuMind API.
Defines clean data validation models for requests and responses.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    """Response model for the /health endpoint."""
    status: str = Field(default="ok", description="Status of the API service")
    service: str = Field(default="DocuMind API", description="Service identifier name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ok",
                "service": "DocuMind API"
            }
        }
    }


class DocumentResponse(BaseModel):
    """Response model for the /upload endpoint."""
    message: str = Field(..., description="Status message of the upload operation")
    filename: str = Field(..., description="Uploaded file name")
    file_type: str = Field(..., description="Detected file type ('pdf' or 'txt')")
    size: int = Field(..., description="File size in bytes")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Document uploaded successfully",
                "filename": "sample.pdf",
                "file_type": "pdf",
                "size": 1048576
            }
        }
    }


class ExtractedDocument(BaseModel):
    """Model representing extracted document text content and metadata."""
    filename: str = Field(..., description="Name of the parsed document")
    pages: int = Field(..., description="Total number of pages in the document (1 for TXT)")
    text: str = Field(..., description="Complete extracted text from the document")

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "document.pdf",
                "pages": 5,
                "text": "Extracted document content..."
            }
        }
    }


class Source(BaseModel):
    """Model representing a reference source for Q&A answers."""
    page: Optional[int] = Field(default=None, description="Page number of the source chunk (if applicable)")
    text: str = Field(..., description="Relevant passage text snippet from the document")

    model_config = {
        "json_schema_extra": {
            "example": {
                "page": 1,
                "text": "DocuMind is an AI-powered document question and answer system."
            }
        }
    }


class QuestionRequest(BaseModel):
    """Request model for the /ask endpoint."""
    question: str = Field(..., description="The user question regarding uploaded documents")

    @field_validator("question")
    @classmethod
    def validate_question_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Question cannot be empty.")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "What is this document about?"
            }
        }
    }


class QuestionResponse(BaseModel):
    """Response model for the /ask endpoint."""
    answer: str = Field(..., description="Generated answer from the document context")
    sources: List[Source] = Field(default_factory=list, description="List of source passages used for the answer")

    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "RAG service not connected. Please connect embeddings and vector store to enable Q&A.",
                "sources": []
            }
        }
    }


class ErrorResponse(BaseModel):
    """Standardized error response model."""
    detail: str = Field(..., description="Detailed description of the error")

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Only PDF and TXT files are supported."
            }
        }
    }
