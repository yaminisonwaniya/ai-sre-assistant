"""Analysis service executing ML classification, spaCy ISO 29148 quality rules, scoring, and DB issue persistence."""
from typing import List, Optional
from sqlalchemy.orm import Session
import spacy

from app.models.requirement import Requirement
from app.models.issue import Issue
from app.nlp.classifier import predict_requirement_type
from app.nlp.quality.rules import analyze_requirement_quality
from app.nlp.quality.scoring import calculate_quality_score

# Load spaCy model lazily
try:
    nlp_model = spacy.load("en_core_web_sm")
except Exception:
    nlp_model = None


class AnalysisService:
    """Service orchestrating requirement analysis and Issue persistence."""

    @classmethod
    def analyze_single_requirement(cls, db: Session, req_id: int) -> Optional[Requirement]:
        """Analyze a single requirement statement, persisting classification, issues, and quality score."""
        req = db.query(Requirement).filter(Requirement.id == req_id).first()
        if not req:
            return None

        # 1. Predict Requirement Type & Subtype
        pred_type, pred_subtype, _ = predict_requirement_type(req.text)
        req.type = pred_type
        req.subtype = pred_subtype

        # 2. Parse text with spaCy doc if available
        doc = nlp_model(req.text) if nlp_model is not None else None

        # 3. Detect ISO/IEC/IEEE 29148 Quality Issues
        detected_issues = analyze_requirement_quality(req.text, req_type=req.type, nlp_doc=doc)

        # 4. Calculate Aggregate Quality Score
        score, label, _ = calculate_quality_score(detected_issues)
        req.quality_score = score
        req.status = "ANALYZED"

        # 5. Clear old issues and persist new Issue records
        db.query(Issue).filter(Issue.requirement_id == req.id).delete()
        for issue_dict in detected_issues:
            issue_obj = Issue(
                requirement_id=req.id,
                category=issue_dict["category"],
                severity=issue_dict["severity"],
                trigger_text=issue_dict.get("trigger_text"),
                explanation=issue_dict["explanation"],
                standard_reference=issue_dict.get("standard_reference", "ISO/IEC/IEEE 29148:2018"),
            )
            db.add(issue_obj)

        db.commit()
        db.refresh(req)
        return req

    @classmethod
    def analyze_project_requirements(cls, db: Session, project_id: int) -> List[Requirement]:
        """Batch analyze all requirements belonging to a project."""
        reqs = db.query(Requirement).filter(Requirement.project_id == project_id).all()
        analyzed_reqs = []
        for req in reqs:
            analyzed = cls.analyze_single_requirement(db, req.id)
            if analyzed:
                analyzed_reqs.append(analyzed)
        return analyzed_reqs
