"""
Q&A Router for DocuMind.
Handles question-answering requests and interfaces with the RAG service.
"""

from fastapi import APIRouter, HTTPException, status
from models.schemas import QuestionRequest, QuestionResponse, ErrorResponse
from services.rag_service import answer_question

router = APIRouter(tags=["Q&A Operations"])


@router.post(
    "/ask",
    response_model=QuestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question about uploaded documents",
    description="Accepts a user question and returns a generated answer with supporting source citations.",
    responses={
        200: {"model": QuestionResponse, "description": "Answer and sources generated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid or empty question"},
        500: {"model": ErrorResponse, "description": "Internal server processing error"},
    },
)
async def ask_question(request: QuestionRequest):
    """
    Process question using the RAG service pipeline and return answer + sources.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty."
        )

    try:
        response = answer_question(
            question=request.question.strip(),
            filename=request.filename
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while generating the answer: {str(e)}"
        )
