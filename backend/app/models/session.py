from datetime import datetime

from sqlalchemy import CheckConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.common import SessionStatus, TimestampMixin


class Session(Base, TimestampMixin):
    """A scheduled learning session between a teacher and a learner."""

    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint("teacher_id != learner_id", name="ck_session_not_self"),
        CheckConstraint("end_time > start_time", name="ck_session_end_after_start"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    learner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)
    exchange_request_id: Mapped[int | None] = mapped_column(
        ForeignKey("exchange_requests.id", ondelete="SET NULL"), nullable=True
    )

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    meeting_link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[SessionStatus] = mapped_column(
        SAEnum(SessionStatus), nullable=False, default=SessionStatus.SCHEDULED
    )

    teacher: Mapped["User"] = relationship(foreign_keys=[teacher_id], back_populates="teaching_sessions")
    learner: Mapped["User"] = relationship(foreign_keys=[learner_id], back_populates="learning_sessions")
    skill: Mapped["Skill"] = relationship()

    reviews: Mapped[list["Review"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    transactions: Mapped[list["CreditTransaction"]] = relationship(back_populates="session")
