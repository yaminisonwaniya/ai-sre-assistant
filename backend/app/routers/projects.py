"""Project REST API endpoints including batch quality analysis."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    ProjectDetailRead,
    ProjectListResponse,
)
from app.schemas.requirement import RequirementRead
from app.services.project_service import ProjectService
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List all requirements engineering projects."""
    items, total = ProjectService.get_all(db, skip=skip, limit=limit)
    return {"items": items, "total": total}


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new SRS project."""
    project = ProjectService.create(db, project_in)
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "requirement_count": 0,
    }


@router.get("/{project_id}", response_model=ProjectDetailRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Fetch project details including its list of requirements."""
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )
    return project


@router.post("/{project_id}/analyze", response_model=List[RequirementRead])
def analyze_project_requirements(project_id: int, db: Session = Depends(get_db)):
    """Batch analyze all requirements in a project."""
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )
    return AnalysisService.analyze_project_requirements(db, project_id)


@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int, project_in: ProjectUpdate, db: Session = Depends(get_db)
):
    """Update project title or description."""
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )
    updated = ProjectService.update(db, project, project_in)
    req_count = len(updated.requirements)
    return {
        "id": updated.id,
        "name": updated.name,
        "description": updated.description,
        "created_at": updated.created_at,
        "updated_at": updated.updated_at,
        "requirement_count": req_count,
    }


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete project and associated requirements."""
    success = ProjectService.delete(db, project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )
    return None
