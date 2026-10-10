"""Pydantic schemas for Issue entity."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class IssueBase(BaseModel):
    category: str
    severity: str
    trigger_text: Optional[str] = None
    explanation: str
    standard_reference: str = "ISO/IEC/IEEE 29148:2018"


class IssueCreate(IssueBase):
    requirement_id: int


class IssueRead(IssueBase):
    id: int
    requirement_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
