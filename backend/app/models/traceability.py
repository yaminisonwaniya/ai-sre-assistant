"""Traceability junction entity mapping requirements to test cases."""
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.base import TimestampMixin


class Traceability(Base, TimestampMixin):
    """Many-to-many junction table linking Requirements and TestCases."""
    
    __tablename__ = "traceability"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    requirement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    test_case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    coverage_type: Mapped[str] = mapped_column(
        String(50), default="DIRECT", nullable=False
    )  # DIRECT, INDIRECT, EDGE_CASE

    # Relationships
    requirement = relationship("Requirement", back_populates="traceability_links")
    test_case = relationship("TestCase", back_populates="traceability_links")

    def __repr__(self) -> str:
        return f"<Traceability(req={self.requirement_id}, tc={self.test_case_id}, type='{self.coverage_type}')>"
