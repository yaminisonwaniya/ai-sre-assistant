"""TestCase entity model generated for requirement verification."""
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.traceability import Traceability


class TestCase(Base, TimestampMixin):
    """Generated software test case for requirement validation."""
    
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    test_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    preconditions: Mapped[str] = mapped_column(Text, nullable=True)
    steps: Mapped[str] = mapped_column(Text, nullable=False)  # JSON formatted or text steps
    expected_result: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    traceability_links: Mapped[List["Traceability"]] = relationship(
        "Traceability", back_populates="test_case", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TestCase(id={self.id}, code='{self.test_code}', title='{self.title}')>"
