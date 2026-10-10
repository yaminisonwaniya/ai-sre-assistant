"""Issue entity representing quality or ambiguity flaws detected in requirements."""
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.requirement import Requirement


class Issue(Base, TimestampMixin):
    """Quality issue detected in a requirement based on ISO/IEC/IEEE 29148 characteristics."""
    
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    requirement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # AMBIGUITY, VAGUENESS, INCOMPLETENESS, NON_TESTABILITY, PASSIVE_VOICE
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False, default="MEDIUM"
    )  # CRITICAL, HIGH, MEDIUM, LOW
    trigger_text: Mapped[str] = mapped_column(Text, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    standard_reference: Mapped[str] = mapped_column(
        String(255), nullable=False, default="ISO/IEC/IEEE 29148:2018"
    )

    # Relationships
    requirement: Mapped["Requirement"] = relationship("Requirement", back_populates="issues")

    def __repr__(self) -> str:
        return f"<Issue(id={self.id}, req={self.requirement_id}, category='{self.category}', severity='{self.severity}')>"
