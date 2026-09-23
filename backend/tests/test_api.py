"""
Unit and integration tests for DocuMind FastAPI backend.
Tests health, document uploads, validations, text extraction, Q&A, and CORS.
"""

import io
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app
from services.document_service import extract_document_text, extract_text_from_pdf, extract_text_from_txt

client = TestClient(app)


def create_sample_pdf_bytes(text_content: str = "DocuMind sample document page.") -> bytes:
    """Helper to generate in-memory valid PDF bytes."""
    writer = PdfWriter()
    page = writer.add_blank_page(width=200, height=200)
    pdf_buffer = io.BytesIO()
    writer.write(pdf_buffer)
    return pdf_buffer.getvalue()


# 1. Test Health Endpoint
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "DocuMind API"


# 2. Test Root Endpoint
def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "DocuMind API"
    assert data["status"] == "online"


# 3. Test Upload Valid TXT & Vector Ingestion
def test_upload_valid_txt(tmp_path):
    txt_content = b"DocuMind is an intelligent document Q&A application powered by Retrieval-Augmented Generation. It uses ChromaDB for persistent vector storage."
    response = client.post(
        "/upload",
        files={"file": ("test_doc.txt", txt_content, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "uploaded and indexed" in data["message"].lower() or "uploaded successfully" in data["message"].lower()
    assert data["filename"] == "test_doc.txt"
    assert data["file_type"] == "txt"
    assert data["size"] == len(txt_content)


# 4. Test Upload Valid PDF & Vector Ingestion
def test_upload_valid_pdf():
    pdf_bytes = create_sample_pdf_bytes("DocuMind PDF sample text.")
    response = client.post(
        "/upload",
        files={"file": ("sample.pdf", pdf_bytes, "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "sample.pdf"
    assert data["file_type"] == "pdf"
    assert data["size"] == len(pdf_bytes)


# 5. Test Upload Unsupported File Type (.exe / .png / .csv)
def test_upload_unsupported_file_type():
    fake_exe = b"MZ\x90\x00\x03\x00\x00\x00"
    response = client.post(
        "/upload",
        files={"file": ("program.exe", fake_exe, "application/octet-stream")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "Only PDF and TXT files are supported" in data["detail"]

    fake_png = b"\x89PNG\r\n\x1a\n"
    response2 = client.post(
        "/upload",
        files={"file": ("image.png", fake_png, "image/png")}
    )
    assert response2.status_code == 400
    assert "Only PDF and TXT files are supported" in response2.json()["detail"]


# 6. Test Upload File Larger Than 20 MB Limit (413)
def test_upload_file_too_large(monkeypatch):
    import routes.upload as upload_module
    monkeypatch.setattr(upload_module, "MAX_FILE_SIZE_BYTES", 1024)
    monkeypatch.setattr(upload_module, "MAX_FILE_SIZE_MB", 1)

    oversized_content = b"A" * 2048  # 2 KB > 1 KB limit
    response = client.post(
        "/upload",
        files={"file": ("large_doc.txt", oversized_content, "text/plain")}
    )
    assert response.status_code == 413
    assert "limit" in response.json()["detail"].lower()


# 7. Test Empty Question to /ask
def test_ask_empty_question():
    response = client.post(
        "/ask",
        json={"question": ""}
    )
    assert response.status_code == 400
    assert "Question cannot be empty" in response.json()["detail"]

    response_whitespace = client.post(
        "/ask",
        json={"question": "   \n\t  "}
    )
    assert response_whitespace.status_code == 400
    assert "Question cannot be empty" in response_whitespace.json()["detail"]


# 8. Test Normal Question to /ask
def test_ask_normal_question():
    # First ensure a known document is uploaded
    doc_text = b"Machine learning allows systems to learn patterns from training data without being explicitly programmed."
    client.post(
        "/upload",
        files={"file": ("ml_intro.txt", doc_text, "text/plain")}
    )

    response = client.post(
        "/ask",
        json={"question": "What is machine learning?", "filename": "ml_intro.txt"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0
    assert data["sources"][0]["filename"] == "ml_intro.txt"


# 9. Test Out-of-Context Question (Anti-Hallucination Fallback)
def test_ask_out_of_context_question():
    response = client.post(
        "/ask",
        json={"question": "What is the population of Jupiter's moon Europa?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "couldn't find" in data["answer"].lower() or "not found" in data["answer"].lower()


# 10. Test CORS Configuration
def test_cors_headers():
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


# 11. Test Document Extraction Services
def test_txt_extraction_service(tmp_path):
    txt_file = tmp_path / "test_extract.txt"
    txt_file.write_text("This is test text for extraction.", encoding="utf-8")
    
    extracted = extract_text_from_txt(txt_file)
    assert extracted.filename == "test_extract.txt"
    assert extracted.pages == 1
    assert extracted.text == "This is test text for extraction."
    assert len(extracted.pages_data) == 1


def test_pdf_extraction_service(tmp_path):
    pdf_bytes = create_sample_pdf_bytes()
    pdf_file = tmp_path / "test_extract.pdf"
    pdf_file.write_bytes(pdf_bytes)

    extracted = extract_text_from_pdf(pdf_file)
    assert extracted.filename == "test_extract.pdf"
    assert extracted.pages == 1
    assert extracted.pages_data is not None


def test_unsupported_extraction_service(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("col1,col2\n1,2", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file extension"):
        extract_document_text(csv_file)
