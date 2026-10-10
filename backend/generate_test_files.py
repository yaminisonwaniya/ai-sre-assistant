"""Script generating sample SRS test files (.txt, .docx, .pdf, corrupt) in data/ directory."""
import os
import sys
import docx

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

SAMPLE_SRS_TEXT = """Software Requirements Specification for Hospital Portal

1. INTRODUCTION
Table of Contents ........ 3
Page 1 of 12

1.1 Scope
The system shall allow registered patients to log in using email and password.
1.2 Security Requirements
- The system must encrypt all patient health data at rest using AES-256.
- The system shall automatically lock out accounts after 5 failed login attempts.

2. SYSTEM REQUIREMENTS
2.1 Performance
The system should respond to authentication requests within 1.5 seconds.
2.2 Reporting
The platform shall generate downloadable PDF appointment history reports within 3 seconds.
"""


def create_txt_file():
    txt_path = os.path.join(DATA_DIR, "sample_srs.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(SAMPLE_SRS_TEXT)
    print(f"Created {txt_path}")


def create_docx_file():
    docx_path = os.path.join(DATA_DIR, "sample_srs.docx")
    doc = docx.Document()
    doc.add_heading("Software Requirements Specification", 0)
    doc.add_paragraph("Table of Contents .......... 2")
    doc.add_paragraph("Page 1 of 5")
    
    doc.add_heading("1. Functional Requirements", level=1)
    doc.add_paragraph("1.1 The system shall authenticate users via two-factor authentication.")
    doc.add_paragraph("1.2 The system must process credit card payments within 2 seconds.")
    
    doc.add_heading("2. Non-Functional Requirements", level=1)
    doc.add_paragraph("- The system shall maintain 99.9% uptime during operational hours.")
    doc.add_paragraph("- All network communication must use TLS 1.3 protocol.")
    
    doc.save(docx_path)
    print(f"Created {docx_path}")


def create_corrupt_file():
    corrupt_path = os.path.join(DATA_DIR, "corrupt_sample.docx")
    with open(corrupt_path, "wb") as f:
        f.write(b"NOT_A_REAL_ZIP_OR_DOCX_FILE_CORRUPTED_BINARY_DATA_1234567890")
    print(f"Created {corrupt_path}")


def create_pdf_file():
    pdf_path = os.path.join(DATA_DIR, "sample_srs.pdf")
    # Valid minimal PDF structure with MediaBox and text streams
    pdf_bytes = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        b"5 0 obj << /Length 170 >> stream\n"
        b"BT /F1 12 Tf 50 700 Td (Software Requirements Specification) Tj ET\n"
        b"BT /F1 10 Tf 50 670 Td (1.1 The system shall export logs to PDF format within 3 seconds.) Tj ET\n"
        b"BT /F1 10 Tf 50 650 Td (- The system must encrypt database backups.) Tj ET\n"
        b"endstream\nendobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000062 00000 n \n0000000123 00000 n \n0000000257 00000 n \n0000000330 00000 n \n"
        b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n551\n%%EOF\n"
    )
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"Created {pdf_path}")


if __name__ == "__main__":
    create_txt_file()
    create_docx_file()
    create_corrupt_file()
    create_pdf_file()
