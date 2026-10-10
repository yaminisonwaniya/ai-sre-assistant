"""Unit and integration tests for Phase 2 requirement processing, noise cleaning, file parsing, and import API endpoints."""
import os
import io
import pytest
from app.nlp.cleaner import clean_document_text, is_page_number_line, is_toc_line, is_heading_line
from app.nlp.splitter import extract_requirements_from_text, contains_requirement_modal
from app.nlp.file_parser import parse_uploaded_file, FileParseError, MAX_FILE_SIZE_BYTES

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "data")


# --- NLP Cleaner & Splitter Unit Tests ---

def test_cleaner_heuristics():
    assert is_page_number_line("Page 1 of 15") is True
    assert is_page_number_line("- 12 -") is True
    assert is_page_number_line("The system shall process requests.") is False

    assert is_toc_line("1.1 System Architecture ........ 14") is True
    assert is_heading_line("1.0 INTRODUCTION") is True


def test_text_splitting_modal_and_list_patterns():
    raw_text = """
    Software Requirements Specification
    Table of Contents ....... 2
    Page 1 of 5

    1.1 System Scope
    The system shall allow patients to log into their account.
    - The system must encrypt stored health records using AES-256.
    1.2 Performance
    The system should respond within 1.5 seconds.
    The software is required to support 500 concurrent connections.
    """
    extracted = extract_requirements_from_text(raw_text)
    assert len(extracted) == 4

    statements = [item["text"] for item in extracted]
    assert "The system shall allow patients to log into their account." in statements
    assert "The system must encrypt stored health records using AES-256." in statements
    assert "The system should respond within 1.5 seconds." in statements
    assert "The software is required to support 500 concurrent connections." in statements


# --- File Parsing Edge Cases ---

def test_parse_txt_file():
    txt_path = os.path.join(DATA_DIR, "sample_srs.txt")
    if not os.path.exists(txt_path):
        pytest.skip("sample_srs.txt not generated yet")
    with open(txt_path, "rb") as f:
        bytes_data = f.read()
    raw_text, reqs = parse_uploaded_file("sample_srs.txt", bytes_data)
    assert len(reqs) > 0


def test_parse_docx_file():
    docx_path = os.path.join(DATA_DIR, "sample_srs.docx")
    if not os.path.exists(docx_path):
        pytest.skip("sample_srs.docx not generated yet")
    with open(docx_path, "rb") as f:
        bytes_data = f.read()
    raw_text, reqs = parse_uploaded_file("sample_srs.docx", bytes_data)
    assert len(reqs) > 0


def test_parse_pdf_file():
    pdf_path = os.path.join(DATA_DIR, "sample_srs.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip("sample_srs.pdf not generated yet")
    with open(pdf_path, "rb") as f:
        bytes_data = f.read()
    raw_text, reqs = parse_uploaded_file("sample_srs.pdf", bytes_data)
    assert len(reqs) > 0


def test_corrupt_docx_error_handling():
    corrupt_bytes = b"INVALID_CORRUPTED_BINARY_HEADER"
    with pytest.raises(FileParseError) as exc_info:
        parse_uploaded_file("corrupt.docx", corrupt_bytes)
    assert "corrupted" in str(exc_info.value).lower() or "failed" in str(exc_info.value).lower()


def test_wrong_file_extension():
    with pytest.raises(FileParseError) as exc_info:
        parse_uploaded_file("document.executable", b"some text")
    assert "unsupported file extension" in str(exc_info.value).lower()


def test_empty_file_error():
    with pytest.raises(FileParseError) as exc_info:
        parse_uploaded_file("empty.txt", b"   ")
    assert "empty" in str(exc_info.value).lower()


def test_file_exceeds_max_size():
    huge_bytes = b"A" * (MAX_FILE_SIZE_BYTES + 1024)
    with pytest.raises(FileParseError) as exc_info:
        parse_uploaded_file("large.txt", huge_bytes)
    assert "exceeds maximum allowed limit" in str(exc_info.value).lower()


# --- API Endpoint Integration Tests ---

def test_import_text_preview_endpoint(client):
    proj_res = client.post("/api/v1/projects", json={"name": "Import Text Proj"})
    proj_id = proj_res.json()["id"]

    payload = {
        "text": "1. The system shall send welcome emails.\n2. The system must verify SMS tokens.",
        "preview": True
    }
    res = client.post(f"/api/v1/projects/{proj_id}/requirements/import-text", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["preview"] is True
    assert data["total_extracted"] == 2
    assert data["items"][0]["req_code"] == "REQ-001"
    assert data["items"][1]["req_code"] == "REQ-002"

    # Verify nothing saved to DB in preview mode
    get_res = client.get(f"/api/v1/projects/{proj_id}/requirements")
    assert get_res.json()["total"] == 0


def test_batch_create_requirements_and_req_code_continuation(client):
    proj_res = client.post("/api/v1/projects", json={"name": "Batch Import Proj"})
    proj_id = proj_res.json()["id"]

    # Add initial requirement REQ-001
    client.post(f"/api/v1/projects/{proj_id}/requirements", json={"text": "Initial requirement statement."})

    # Batch import 2 requirements -> should be assigned REQ-002 and REQ-003
    batch_payload = {
        "requirements": [
            {"text": "Extracted requirement statement 1", "type": "FUNCTIONAL"},
            {"text": "Extracted requirement statement 2", "type": "NON_FUNCTIONAL"}
        ]
    }
    batch_res = client.post(f"/api/v1/projects/{proj_id}/requirements/batch", json=batch_payload)
    assert batch_res.status_code == 201
    saved_items = batch_res.json()
    assert len(saved_items) == 2
    assert saved_items[0]["req_code"] == "REQ-002"
    assert saved_items[1]["req_code"] == "REQ-003"


def test_import_file_upload_endpoint(client):
    proj_res = client.post("/api/v1/projects", json={"name": "File Upload Proj"})
    proj_id = proj_res.json()["id"]

    file_content = b"The system shall authenticate users using OAuth 2.0."
    files = {"file": ("test_srs.txt", file_content, "text/plain")}

    res = client.post(
        f"/api/v1/projects/{proj_id}/requirements/import?preview=true",
        files=files
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_extracted"] == 1
    assert data["items"][0]["req_code"] == "REQ-001"
