"""Pydantic schemas for requirement extraction and import endpoints."""
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.requirement import RequirementRead


class RequirementImportTextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw SRS text statement or document content")
    preview: bool = Field(True, description="If true, returns candidate list without saving to DB")


class ExtractedRequirementItem(BaseModel):
    req_code: str = Field(..., description="Auto-assigned requirement code e.g. REQ-001")
    text: str = Field(..., description="Extracted requirement text statement")
    type: str = Field("UNCLASSIFIED", description="Default classification type")
    subtype: str = Field("GENERAL", description="Default subtype")
    source_reference: Optional[str] = Field(None, description="Source line or section reference")


class RequirementImportResponse(BaseModel):
    preview: bool
    total_extracted: int
    items: List[ExtractedRequirementItem]
    saved_items: Optional[List[RequirementRead]] = None


class BatchRequirementItem(BaseModel):
    req_code: Optional[str] = None
    text: str
    type: str = "UNCLASSIFIED"
    subtype: str = "GENERAL"
    status: str = "DRAFT"


class BatchRequirementCreateRequest(BaseModel):
    requirements: List[BatchRequirementItem]
