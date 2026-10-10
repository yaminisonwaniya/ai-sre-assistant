"""Pydantic schemas for TestCase entity."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TestCaseBase(BaseModel):
    test_code: str
    title: str
    description: Optional[str] = None
    preconditions: Optional[str] = None
    steps: str
    expected_result: str


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseRead(TestCaseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
