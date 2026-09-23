"""
DocuMind - AI Document Q&A Backend.
FastAPI Application Entry Point.
"""

import os
from typing import List
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv

from models.schemas import HealthResponse, ErrorResponse
from routes.upload import router as upload_router
from routes.qa import router as qa_router

# Load environment variables
load_dotenv()

# App Metadata
app = FastAPI(
    title="DocuMind API",
    description="FastAPI backend foundation for DocuMind AI Document Q&A (RAG)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
# Restricting to explicit local frontend development origins by default
raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
)
allowed_origins: List[str] = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers to ensure consistent error format and no stack trace leaks
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extract readable message from validation errors
    errors = exc.errors()
    first_msg = errors[0].get("msg", "Invalid request parameters.") if errors else "Validation error."
    # Clean up custom pydantic error prefix if present
    if first_msg.startswith("Value error, "):
        first_msg = first_msg[len("Value error, "):]

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": first_msg},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Prevent stack traces from leaking to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )


# Health Endpoint
@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=["System"],
    summary="Health Check",
    description="Verifies the operational status of the DocuMind API.",
)
async def health_check():
    """Health check endpoint to verify backend service status."""
    return HealthResponse(status="ok", service="DocuMind API")


# Root Endpoint
@app.get(
    "/",
    tags=["System"],
    summary="Root Information",
)
async def root():
    return {
        "service": "DocuMind API",
        "status": "online",
        "docs": "/docs",
        "health": "/health"
    }


# Include Routers
app.include_router(upload_router)
app.include_router(qa_router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
