"""Pydantic schemas for SimilarityLink entity."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SimilarityLinkBase(BaseModel):
    source_req_id: int
    target_req_id: int
    similarity_score: float
    link_type: str = "DUPLICATE"


class SimilarityLinkCreate(SimilarityLinkBase):
    pass


class SimilarityLinkRead(SimilarityLinkBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
