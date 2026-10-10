"""Service layer for Project database operations."""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.project import Project
from app.models.requirement import Requirement
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Business logic for Project CRUD."""

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[dict], int]:
        """Fetch all projects with requirement counts."""
        total = db.query(Project).count()
        projects = db.query(Project).order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for project in projects:
            req_count = db.query(Requirement).filter(Requirement.project_id == project.id).count()
            result.append({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "requirement_count": req_count,
            })
        return result, total

    @staticmethod
    def get_by_id(db: Session, project_id: int) -> Optional[Project]:
        """Fetch a single project by ID."""
        return db.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def create(db: Session, project_in: ProjectCreate) -> Project:
        """Create a new project."""
        project = Project(
            name=project_in.name,
            description=project_in.description
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def update(db: Session, project: Project, project_in: ProjectUpdate) -> Project:
        """Update an existing project."""
        update_data = project_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete(db: Session, project_id: int) -> bool:
        """Delete a project by ID."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return False
        db.delete(project)
        db.commit()
        return True
