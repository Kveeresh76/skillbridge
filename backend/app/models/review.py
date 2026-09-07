from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.common import TimestampMixin


class Review(Base, TimestampMixin):
    """A 1-5 star rating (with optional text) left after a completed session."""

    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
        CheckConstraint("reviewer_id != reviewee_id", name="ck_review_not_self"),
        # One review per (session, reviewer) — each side of a session can rate once.
        UniqueConstraint("session_id", "reviewer_id", name="uq_review_per_session_reviewer"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reviewee_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    session: Mapped["Session"] = relationship(back_populates="reviews")
    reviewer: Mapped["User"] = relationship(foreign_keys=[reviewer_id], back_populates="reviews_given")
    reviewee: Mapped["User"] = relationship(foreign_keys=[reviewee_id], back_populates="reviews_received")
