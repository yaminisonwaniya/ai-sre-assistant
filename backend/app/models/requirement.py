"""Requirement entity model storing individual SRS requirement text, classification, and quality scores."""
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.issue import Issue
    from app.models.similarity_link import SimilarityLink
    from app.models.traceability import Traceability


class Requirement(Base, TimestampMixin):
    """Requirement ORM model."""
    
    __tablename__ = "requirements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    req_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(
        String(50), default="UNCLASSIFIED", nullable=False
    )  # FUNCTIONAL, NON_FUNCTIONAL, UNCLASSIFIED
    subtype: Mapped[str] = mapped_column(
        String(100), default="GENERAL", nullable=True
    )  # PERFORMANCE, SECURITY, RELIABILITY, USABILITY, ACCESSIBILITY, etc.
    quality_score: Mapped[float] = mapped_column(
        Float, default=100.0, nullable=False
    )  # 0.0 to 100.0
    status: Mapped[str] = mapped_column(
        String(50), default="DRAFT", nullable=False
    )  # DRAFT, ANALYZED, REVIEWED, APPROVED

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="requirements")
    issues: Mapped[List["Issue"]] = relationship(
        "Issue", back_populates="requirement", cascade="all, delete-orphan"
    )
    similarity_links_source: Mapped[List["SimilarityLink"]] = relationship(
        "SimilarityLink",
        foreign_keys="[SimilarityLink.source_req_id]",
        back_populates="source_req",
        cascade="all, delete-orphan"
    )
    similarity_links_target: Mapped[List["SimilarityLink"]] = relationship(
        "SimilarityLink",
        foreign_keys="[SimilarityLink.target_req_id]",
        back_populates="target_req",
        cascade="all, delete-orphan"
    )
    traceability_links: Mapped[List["Traceability"]] = relationship(
        "Traceability", back_populates="requirement", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Requirement(id={self.id}, code='{self.req_code}', type='{self.type}')>"
