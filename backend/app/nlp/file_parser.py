"""File parser for TXT, DOCX, and PDF documents with file validation and error handling."""
import io
import os
from typing import Tuple, List, Dict, Any
from app.nlp.splitter import extract_requirements_from_text

# Maximum allowed file size limit (5 MB)
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".txt", ".docx", ".pdf"}


class FileParseError(Exception):
    """Custom exception raised when file parsing fails."""
    pass


def parse_txt_content(content_bytes: bytes) -> str:
    """Parse plain text content with UTF-8 / Latin-1 fallback."""
    try:
        return content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return content_bytes.decode("latin-1")
        except Exception as e:
            raise FileParseError(f"Unable to decode text file: {str(e)}")


def parse_docx_content(content_bytes: bytes) -> str:
    """Parse Microsoft Word (.docx) document content using python-docx."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(content_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        raise FileParseError(f"Failed to parse DOCX file. File may be corrupted or invalid: {str(e)}")


def parse_pdf_content(content_bytes: bytes) -> str:
    """Parse PDF document content using pdfplumber."""
    try:
        import pdfplumber
        extracted_pages = []
        with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
            if not pdf.pages:
                raise FileParseError("PDF document contains no pages.")
            for i, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    extracted_pages.append(page_text)

        full_text = "\n".join(extracted_pages).strip()
        if not full_text:
            raise FileParseError("PDF file appears to be scanned or empty. Text extraction yielded no characters.")
        return full_text
    except FileParseError:
        raise
    except Exception as e:
        raise FileParseError(f"Failed to parse PDF document: {str(e)}")


def parse_uploaded_file(filename: str, content_bytes: bytes) -> Tuple[str, List[Dict[str, Any]]]:
    """Validate and parse uploaded file bytes, returning full text and extracted requirements."""
    if len(content_bytes) > MAX_FILE_SIZE_BYTES:
        raise FileParseError(f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB.")

    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise FileParseError(f"Unsupported file extension '{ext}'. Allowed extensions: .txt, .docx, .pdf")

    if not content_bytes or len(content_bytes.strip()) == 0:
        raise FileParseError("Uploaded file is empty.")

    if ext == ".txt":
        raw_text = parse_txt_content(content_bytes)
    elif ext == ".docx":
        raw_text = parse_docx_content(content_bytes)
    elif ext == ".pdf":
        raw_text = parse_pdf_content(content_bytes)
    else:
        raise FileParseError(f"Unsupported file format: {ext}")

    requirements = extract_requirements_from_text(raw_text)
    return raw_text, requirements
