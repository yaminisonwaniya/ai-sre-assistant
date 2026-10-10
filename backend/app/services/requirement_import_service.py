"""Service layer orchestrating requirement import, text processing, auto REQ ID assignment, and batch persistence."""
import re
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.requirement import Requirement
from app.nlp.splitter import extract_requirements_from_text
from app.nlp.file_parser import parse_uploaded_file, FileParseError
from app.schemas.import_schema import (
    ExtractedRequirementItem,
    RequirementImportResponse,
    BatchRequirementItem,
)
from app.schemas.requirement import RequirementRead


class RequirementImportService:
    """Service layer for importing, extracting, and auto-coding requirements."""

    @staticmethod
    def get_next_req_code_number(db: Session, project_id: int) -> int:
        """Find the current highest numeric REQ suffix for a project and return next number."""
        reqs = db.query(Requirement.req_code).filter(Requirement.project_id == project_id).all()
        max_num = 0
        for (code,) in reqs:
            match = re.search(r"REQ-(\d+)", code, re.IGNORECASE)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        return max_num + 1

    @classmethod
    def assign_req_codes(
        cls, db: Session, project_id: int, extracted_items: List[Dict[str, Any]]
    ) -> List[ExtractedRequirementItem]:
        """Assign incremental REQ codes (REQ-001, REQ-002...) continuing from highest existing project code."""
        start_num = cls.get_next_req_code_number(db, project_id)
        result = []

        for idx, item in enumerate(extracted_items):
            code_num = start_num + idx
            req_code = f"REQ-{code_num:03d}"
            result.append(
                ExtractedRequirementItem(
                    req_code=req_code,
                    text=item["text"],
                    type="UNCLASSIFIED",
                    subtype="GENERAL",
                    source_reference=item.get("source_reference"),
                )
            )

        return result

    @classmethod
    def process_text_import(
        cls, db: Session, project_id: int, raw_text: str, preview: bool = True
    ) -> RequirementImportResponse:
        """Process raw SRS text input into candidate requirements."""
        extracted = extract_requirements_from_text(raw_text)
        candidate_items = cls.assign_req_codes(db, project_id, extracted)

        saved_items = None
        if not preview and candidate_items:
            saved_items = cls.save_batch(db, project_id, candidate_items)

        return RequirementImportResponse(
            preview=preview,
            total_extracted=len(candidate_items),
            items=candidate_items,
            saved_items=saved_items,
        )

    @classmethod
    def process_file_import(
        cls, db: Session, project_id: int, filename: str, content_bytes: bytes, preview: bool = True
    ) -> RequirementImportResponse:
        """Process uploaded file (.txt, .docx, .pdf) into candidate requirements."""
        _, extracted = parse_uploaded_file(filename, content_bytes)
        candidate_items = cls.assign_req_codes(db, project_id, extracted)

        saved_items = None
        if not preview and candidate_items:
            saved_items = cls.save_batch(db, project_id, candidate_items)

        return RequirementImportResponse(
            preview=preview,
            total_extracted=len(candidate_items),
            items=candidate_items,
            saved_items=saved_items,
        )

    @classmethod
    def save_batch(
        cls, db: Session, project_id: int, items: List[Any]
    ) -> List[RequirementRead]:
        """Persist a list of confirmed requirement items into the database."""
        start_num = cls.get_next_req_code_number(db, project_id)
        saved_db_items = []

        for idx, item in enumerate(items):
            # Item can be ExtractedRequirementItem or BatchRequirementItem
            item_dict = item.model_dump() if hasattr(item, "model_dump") else item
            req_code = item_dict.get("req_code")
            if not req_code:
                code_num = start_num + idx
                req_code = f"REQ-{code_num:03d}"

            db_req = Requirement(
                project_id=project_id,
                req_code=req_code,
                text=item_dict["text"],
                type=item_dict.get("type", "UNCLASSIFIED"),
                subtype=item_dict.get("subtype", "GENERAL"),
                quality_score=100.0,
                status=item_dict.get("status", "DRAFT"),
            )
            db.add(db_req)
            saved_db_items.append(db_req)

        db.commit()
        for req in saved_db_items:
            db.refresh(req)

        return [RequirementRead.model_validate(r) for r in saved_db_items]
