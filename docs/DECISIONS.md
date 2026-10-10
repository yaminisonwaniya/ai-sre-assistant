# Architectural Decision Records (ADR)

## ADR 001: Clean Architecture Layering
- **Status**: Accepted
- **Context**: The AI-Powered Software Requirements Engineering Assistant requires clear separation of concerns to allow baseline rule-based NLP algorithms and future LLM models to operate without tight coupling to API schemas or database models.
- **Decision**: Separate backend code into explicit modules:
  - `routers/`: Endpoint definition & HTTP parameter validation.
  - `services/`: Business logic, database query encapsulation, and orchestrations.
  - `models/`: SQLAlchemy ORM entity definitions.
  - `schemas/`: Pydantic data transfer objects (DTOs) for request/response serialization.
  - `nlp/`: SpaCy/scikit-learn requirement analysis modules.
  - `llm/`: Abstracted `LLMProvider` interface and implementations.

## ADR 002: Relational Schema & Database Portability
- **Status**: Accepted
- **Context**: Local development requires zero-setup SQLite, while production environments may target PostgreSQL.
- **Decision**: Use SQLAlchemy 2.0 with standard column types (`String`, `Integer`, `Float`, `Text`, `DateTime`) and explicit foreign key relationships (`CASCADE` deletes). Avoid database-specific dialects in ORM entity definitions.

## ADR 003: LLM Decoupling and Rule-Based Baseline First
- **Status**: Accepted
- **Context**: Core functionality must not depend on cloud API availability, network access, or paid LLM tokens.
- **Decision**: Rule-based heuristic analysis (spaCy + regex + ISO/IEC/IEEE 29148 standards) acts as the foundation. LLMs provide optional enhancement layers with graceful fallback.

## ADR 004: Requirement Extraction & Document Noise Cleaning Heuristics
- **Status**: Accepted
- **Context**: Raw SRS text and uploaded documents (.txt, .docx, .pdf) contain non-requirement noise such as Table of Contents entries, page numbers, header/footers, and structural section titles.
- **Decision**: Implement a two-stage extraction pipeline in `app/nlp/`:
  1. **Noise Cleaning (`cleaner.py`)**:
     - Page numbers: Strip patterns like `Page X of Y`, `- 12 -`.
     - Table of Contents: Strip dot-leader patterns (`1.1 Scope ........ 14`).
     - Section headings: Exclude standalone structural section headers (`1.0 INTRODUCTION`, `SYSTEM OVERVIEW`).
  2. **Sentence Splitting & Filtering (`splitter.py`)**:
     - Extract list items starting with numbered prefixes (`1.1`, `REQ-01`) or bullet symbols (`-`, `*`, `•`).
     - Detect requirement statements containing modal verbs (`shall`, `should`, `must`, `will`, `can`, `is required to`).
     - Filter out short candidates (< 3 words) or non-modal headings to avoid false positives.
  3. **File Parser & Size Limits (`file_parser.py`)**:
     - Support `.txt`, `.docx` (`python-docx`), and `.pdf` (`pdfplumber`).
     - Enforce a strict 5MB maximum file size limit.
     - Gracefully handle corrupted files, empty files, or scanned PDFs by returning explicit `HTTP 400 Bad Request` diagnostic messages.
