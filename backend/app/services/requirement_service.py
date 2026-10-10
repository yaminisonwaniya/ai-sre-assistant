"""Service layer for Requirement database operations."""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.requirement import Requirement
from app.schemas.requirement import RequirementCreate, RequirementUpdate


class RequirementService:
    """Business logic for Requirement CRUD & code generation."""

    @staticmethod
    def generate_req_code(db: Session, project_id: int) -> str:
        """Auto-generate incremental requirement code (REQ-001, REQ-002, etc.)."""
        count = db.query(Requirement).filter(Requirement.project_id == project_id).count()
        return f"REQ-{(count + 1):03d}"

    @staticmethod
    def get_all(
        db: Session,
        project_id: Optional[int] = None,
        req_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Requirement], int]:
        """Fetch requirements with optional filtering."""
        query = db.query(Requirement)
        if project_id is not None:
            query = query.filter(Requirement.project_id == project_id)
        if req_type:
            query = query.filter(Requirement.type == req_type.upper())
        if status:
            query = query.filter(Requirement.status == status.upper())

        total = query.count()
        requirements = query.order_by(Requirement.id.asc()).offset(skip).limit(limit).all()
        return requirements, total

    @staticmethod
    def get_by_id(db: Session, req_id: int) -> Optional[Requirement]:
        """Fetch a requirement by ID."""
        return db.query(Requirement).filter(Requirement.id == req_id).first()

    @staticmethod
    def create(db: Session, project_id: int, req_in: RequirementCreate) -> Requirement:
        """Create a new requirement under a project."""
        req_code = req_in.req_code or RequirementService.generate_req_code(db, project_id)
        requirement = Requirement(
            project_id=project_id,
            req_code=req_code,
            text=req_in.text,
            type=req_in.type,
            subtype=req_in.subtype,
            quality_score=req_in.quality_score,
            status=req_in.status
        )
        db.add(requirement)
        db.commit()
        db.refresh(requirement)
        return requirement

    @staticmethod
    def update(db: Session, requirement: Requirement, req_in: RequirementUpdate) -> Requirement:
        """Update an existing requirement."""
        update_data = req_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(requirement, field, value)
        db.commit()
        db.refresh(requirement)
        return requirement

    @staticmethod
    def delete(db: Session, req_id: int) -> bool:
        """Delete a requirement by ID."""
        req = db.query(Requirement).filter(Requirement.id == req_id).first()
        if not req:
            return False
        db.delete(req)
        db.commit()
        return True
