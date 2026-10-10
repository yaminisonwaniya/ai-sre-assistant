"""Pydantic schemas for Requirement CRUD operations."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.issue import IssueRead


class RequirementBase(BaseModel):
    text: str = Field(..., min_length=1, description="Requirement text statement")
    type: str = Field("UNCLASSIFIED", description="Requirement category: FUNCTIONAL, NON_FUNCTIONAL, etc.")
    subtype: Optional[str] = Field("GENERAL", description="Subcategory: PERFORMANCE, SECURITY, RELIABILITY, etc.")
    quality_score: float = Field(100.0, ge=0.0, le=100.0, description="Quality score percentage")
    status: str = Field("DRAFT", description="Workflow state: DRAFT, ANALYZED, REVIEWED, APPROVED")


class RequirementCreate(RequirementBase):
    req_code: Optional[str] = Field(None, description="Optional code like REQ-001; auto-generated if omitted")


class RequirementUpdate(BaseModel):
    text: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    quality_score: Optional[float] = None
    status: Optional[str] = None


class RequirementRead(RequirementBase):
    id: int
    project_id: int
    req_code: str
    created_at: datetime
    updated_at: datetime
    issues: List[IssueRead] = []

    model_config = ConfigDict(from_attributes=True)


class RequirementListResponse(BaseModel):
    items: List[RequirementRead]
    total: int
    page: int
    size: int
