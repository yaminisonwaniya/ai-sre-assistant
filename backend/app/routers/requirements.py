"""Requirement REST API endpoints including text/file import, batch operations, and quality analysis."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.requirement import (
    RequirementCreate,
    RequirementUpdate,
    RequirementRead,
    RequirementListResponse,
)
from app.schemas.import_schema import (
    RequirementImportTextRequest,
    RequirementImportResponse,
    BatchRequirementCreateRequest,
)
from app.services.project_service import ProjectService
from app.services.requirement_service import RequirementService
from app.services.requirement_import_service import RequirementImportService
from app.services.analysis_service import AnalysisService
from app.nlp.file_parser import FileParseError

router = APIRouter(tags=["Requirements"])


@router.get("/api/v1/projects/{project_id}/requirements", response_model=RequirementListResponse)
def list_project_requirements(
    project_id: int,
    req_type: Optional[str] = Query(None, description="Filter by type (e.g. FUNCTIONAL, NON_FUNCTIONAL)"),
    req_status: Optional[str] = Query(None, alias="status", description="Filter by status (DRAFT, ANALYZED)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List requirements belonging to a specific project with filtering and pagination."""
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )
    items, total = RequirementService.get_all(
        db, project_id=project_id, req_type=req_type, status=req_status, skip=skip, limit=limit
    )
    return {"items": items, "total": total, "page": (skip // limit) + 1, "size": limit}


@router.post(
    "/api/v1/projects/{project_id}/requirements",
    response_model=RequirementRead,
    status_code=status.HTTP_201_CREATED,
)
def create_requirement(
    project_id: int, req_in: RequirementCreate, db: Session = Depends(get_db)
):
    """Create a single requirement under a specific project."""
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )
    return RequirementService.create(db, project_id, req_in)


@router.post(
    "/api/v1/projects/{project_id}/requirements/import",
    response_model=RequirementImportResponse,
    status_code=status.HTTP_200_OK,
)
async def import_requirements(
    project_id: int,
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    preview: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Extract individual requirements from raw text or uploaded document (.txt, .docx, .pdf)."""
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    try:
        if file is not None:
            content_bytes = await file.read()
            return RequirementImportService.process_file_import(
                db, project_id, file.filename, content_bytes, preview=preview
            )
        elif text is not None and text.strip():
            return RequirementImportService.process_text_import(
                db, project_id, text, preview=preview
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either 'file' upload or non-empty 'text' body must be provided.",
            )
    except FileParseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/api/v1/projects/{project_id}/requirements/import-text",
    response_model=RequirementImportResponse,
    status_code=status.HTTP_200_OK,
)
def import_requirements_json(
    project_id: int,
    payload: RequirementImportTextRequest,
    db: Session = Depends(get_db),
):
    """JSON endpoint for raw text requirement extraction."""
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    return RequirementImportService.process_text_import(
        db, project_id, payload.text, preview=payload.preview
    )


@router.post(
    "/api/v1/projects/{project_id}/requirements/batch",
    response_model=List[RequirementRead],
    status_code=status.HTTP_201_CREATED,
)
def batch_create_requirements(
    project_id: int,
    payload: BatchRequirementCreateRequest,
    db: Session = Depends(get_db),
):
    """Save an array of confirmed/edited requirement statements from preview step."""
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found",
        )

    if not payload.requirements:
        return []

    return RequirementImportService.save_batch(db, project_id, payload.requirements)


@router.post("/api/v1/requirements/{req_id}/analyze", response_model=RequirementRead)
def analyze_requirement(req_id: int, db: Session = Depends(get_db)):
    """Analyze single requirement: ML classification, ISO 29148 rule checks, scoring, and issue persistence."""
    req = AnalysisService.analyze_single_requirement(db, req_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID {req_id} not found",
        )
    return req


@router.get("/api/v1/requirements/{req_id}", response_model=RequirementRead)
def get_requirement(req_id: int, db: Session = Depends(get_db)):
    """Fetch a single requirement by ID."""
    req = RequirementService.get_by_id(db, req_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID {req_id} not found",
        )
    return req


@router.put("/api/v1/requirements/{req_id}", response_model=RequirementRead)
def update_requirement(
    req_id: int, req_in: RequirementUpdate, db: Session = Depends(get_db)
):
    """Update requirement text, classification, or quality score."""
    req = RequirementService.get_by_id(db, req_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID {req_id} not found",
        )
    return RequirementService.update(db, req, req_in)


@router.delete("/api/v1/requirements/{req_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_requirement(req_id: int, db: Session = Depends(get_db)):
    """Delete a requirement."""
    success = RequirementService.delete(db, req_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement with ID {req_id} not found",
        )
    return None
