"""SimilarityLink model for tracking duplicate or related requirements."""
from typing import TYPE_CHECKING
from sqlalchemy import Float, String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.requirement import Requirement


class SimilarityLink(Base, TimestampMixin):
    """Pairwise similarity link between requirements."""
    
    __tablename__ = "similarity_links"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    source_req_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_req_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False, index=True
    )
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    link_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="DUPLICATE"
    )  # DUPLICATE, RELATED, CONFLICT

    # Relationships
    source_req: Mapped["Requirement"] = relationship(
        "Requirement", foreign_keys=[source_req_id], back_populates="similarity_links_source"
    )
    target_req: Mapped["Requirement"] = relationship(
        "Requirement", foreign_keys=[target_req_id], back_populates="similarity_links_target"
    )

    def __repr__(self) -> str:
        return f"<SimilarityLink(id={self.id}, source={self.source_req_id}, target={self.target_req_id}, score={self.similarity_score})>"
