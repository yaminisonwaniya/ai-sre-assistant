# AI-Powered Software Requirements Engineering Assistant

An intelligent software engineering platform for analyzing, quality-checking, classifying, and managing Software Requirements Specifications (SRS).

---

## 🌟 Key Features

### Phase 1: Foundation
- **Backend API**: FastAPI REST endpoints for Projects and Requirements CRUD with SQLite/PostgreSQL compatibility.
- **Frontend Dashboard**: React + Vite single page application with glassmorphic styling, project overview, requirement list views, and category filtering.
- **Database Architecture**: SQLAlchemy 2.0 ORM entities for `Project`, `Requirement`, `Issue`, `SimilarityLink`, `TestCase`, and `Traceability`.

### Phase 2: Requirement Processing & SRS Import
- **Multi-Format Document Parser**: Extracts requirements from plain text (`.txt`), Microsoft Word (`.docx`), and PDF (`.pdf`).
- **Document Noise Cleaner**: Strips Table of Contents, page numbers, header/footers, and structural section titles.
- **Auto REQ Code Assignment**: Incremental REQ codes (`REQ-001`, `REQ-002`, ...) continuing from the project's highest code.
- **2-Step Interactive Preview/Edit UI**: Interactive preview table to edit statements, delete false positives, and confirm batch import.

### Phase 3A: Core Analysis Backend
- **ML Requirement Classifier**: TF-IDF + Logistic Regression model trained on the **PROMISE NFR Dataset** (969 samples) classifying Functional vs Non-Functional requirements and quality subcategories.
- **ISO/IEC/IEEE 29148 Quality Analyzer**: Rule-based spaCy dependency parser detecting vague lexicon, passive voice syntax, missing subject actor, missing measurable criteria, non-atomic compound statements, and untestable wording.
- **Explainable Quality Scoring Engine**: Computes sub-scores for Unambiguous (30%), Verifiable (30%), Complete (20%), and Atomic (20%) weighted criteria (0-100 score with `GOOD`, `NEEDS_IMPROVEMENT`, `POOR` status labels).

### Phase 3B: Analysis Dashboard Frontend
- **Interactive Quality Table & Badges**: Requirements table displaying REQ code, type badges, quality score badges (`GOOD`, `NEEDS_IMPROVEMENT`, `POOR`), and issue severity indicators (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- **Multi-Criteria Filter Toolbar**: Filter requirements dynamically by Type, Quality Label, and Severity.
- **"Analyze Project Quality" Action**: Batch triggers backend quality analysis with real-time loading spinners and error handling.
- **Requirement Detail Drawer**: Slide-over panel presenting the requirement text statement with **highlighted trigger words** in red/amber, detailed issue cards, explanation, and exact **ISO/IEC/IEEE 29148 standard references**.
- **Recharts Analytics Dashboard**:
  - Quality Score Distribution (Histogram / Bar chart)
  - Issues by ISO 29148 Category (Bar chart)
  - Functional vs Non-Functional Classification (Pie chart)

---

## 📁 Project Structure

```
ai_sre_assistant/
├── backend/
│   ├── app/
│   │   ├── config.py             # Environment configuration
│   │   ├── main.py               # FastAPI app entry point
│   │   ├── db/                   # SQLAlchemy database setup & sessions
│   │   ├── models/               # ORM entities (Project, Requirement, Issue, SimilarityLink, TestCase, Traceability)
│   │   ├── schemas/              # Pydantic data schemas
│   │   ├── services/             # Business logic layer (Project, Requirement, Import, Analysis)
│   │   ├── routers/              # REST API endpoints (/health, /projects, /requirements)
│   │   └── nlp/
│   │       ├── cleaner.py        # Noise cleaner heuristics
│   │       ├── splitter.py       # Modal & list sentence extractor
│   │       ├── file_parser.py    # TXT, DOCX, PDF readers
│   │       ├── classifier/       # ML Classifier (train.py, predict.py)
│   │       └── quality/          # ISO 29148 rule engine & scoring
│   ├── scripts/
│   │   ├── fetch_promise_dataset.py # PROMISE dataset downloader
│   │   └── generate_test_files.py
│   ├── tests/                    # Pytest test suite (40 unit & integration tests)
│   ├── seed.py                   # Data seeding script
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api/                  # API client wrapper
│   │   ├── components/           # Navbar, ProjectCard, RequirementCard, QualityBadge, DetailDrawer, AnalyticsCharts
│   │   ├── pages/                # ProjectListPage, ProjectDetailPage
│   │   ├── App.jsx               # Navigation state container
│   │   └── index.css             # UI design system tokens & styles
│   ├── package.json              # React, Vite & Recharts dependencies
│   └── vite.config.js            # Vite configuration with API proxy
├── data/
│   └── promise_nfr.csv           # PROMISE NFR dataset (969 samples)
├── docs/
│   ├── DECISIONS.md              # Architectural Decision Records (ADR 001 - ADR 004)
│   ├── SCORING.md                # ISO 29148 scoring formula specification
│   └── evaluation/
│       └── report.md             # ML classification evaluation metrics & confusion matrix
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Backend Setup & Quality Analysis

```bash
cd backend

# Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies & spaCy language model
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Download PROMISE NFR dataset & train ML classifier
python scripts/fetch_promise_dataset.py
python app/nlp/classifier/train.py

# Seed database with sample SRS requirements
python seed.py

# Run full Pytest test suite (40 tests)
python -m pytest tests -v

# Start FastAPI dev server
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Analysis Dashboard

In a separate terminal:
```bash
cd frontend

# Install Node packages
npm install

# Start Vite dev server
npm run dev
```
1. Open `http://localhost:5173` in your browser.
2. Click on the seeded project **Healthcare Patient Portal SRS**.
3. Click **"Analyze Project Quality"** to run batch ML classification and ISO 29148 quality rules.
4. View real-time Recharts analytics (Score Distribution, Issues by Category, Classification).
5. Filter by Type, Quality Label (`GOOD`, `NEEDS_IMPROVEMENT`, `POOR`), or Severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
6. Click any requirement card to open the **Detail Drawer** showing highlighted trigger words, explanations, and ISO/IEC/IEEE 29148 standard references.
