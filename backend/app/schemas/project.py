"""Pydantic schemas for Project CRUD operations."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.requirement import RequirementRead


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project or SRS document title")
    description: Optional[str] = Field(None, description="Detailed project description or scope")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    requirement_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailRead(ProjectRead):
    requirements: List[RequirementRead] = []


class ProjectListResponse(BaseModel):
    items: List[ProjectRead]
    total: int
