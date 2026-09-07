from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.common import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("skill_credits >= 0", name="ck_users_credits_non_negative"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Denormalized balance for fast reads. It must only ever change alongside
    # a corresponding CreditTransaction row (see services/credit_service.py) —
    # never mutate this column directly elsewhere.
    skill_credits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # --- Relationships ---
    profile: Mapped["Profile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    skills: Mapped[list["UserSkill"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    sent_requests: Mapped[list["ExchangeRequest"]] = relationship(
        foreign_keys="ExchangeRequest.sender_id", back_populates="sender"
    )
    received_requests: Mapped[list["ExchangeRequest"]] = relationship(
        foreign_keys="ExchangeRequest.receiver_id", back_populates="receiver"
    )

    teaching_sessions: Mapped[list["Session"]] = relationship(
        foreign_keys="Session.teacher_id", back_populates="teacher"
    )
    learning_sessions: Mapped[list["Session"]] = relationship(
        foreign_keys="Session.learner_id", back_populates="learner"
    )

    reviews_given: Mapped[list["Review"]] = relationship(
        foreign_keys="Review.reviewer_id", back_populates="reviewer"
    )
    reviews_received: Mapped[list["Review"]] = relationship(
        foreign_keys="Review.reviewee_id", back_populates="reviewee"
    )

    transactions: Mapped[list["CreditTransaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    messages_sent: Mapped[list["Message"]] = relationship(
        foreign_keys="Message.sender_id", back_populates="sender"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User id={self.id} username={self.username!r}>"
