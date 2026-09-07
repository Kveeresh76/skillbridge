import enum
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Adds created_at / updated_at columns to any model that inherits it."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SkillLevel(str, enum.Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class UserSkillType(str, enum.Enum):
    OFFERED = "OFFERED"
    WANTED = "WANTED"


class TransactionType(str, enum.Enum):
    EARNED = "EARNED"
    SPENT = "SPENT"
    BONUS = "BONUS"
    REFUND = "REFUND"
    ADJUSTMENT = "ADJUSTMENT"


class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class SessionStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class NotificationType(str, enum.Enum):
    NEW_REQUEST = "NEW_REQUEST"
    REQUEST_ACCEPTED = "REQUEST_ACCEPTED"
    REQUEST_REJECTED = "REQUEST_REJECTED"
    NEW_MESSAGE = "NEW_MESSAGE"
    SESSION_SCHEDULED = "SESSION_SCHEDULED"
    SESSION_REMINDER = "SESSION_REMINDER"
    SESSION_COMPLETED = "SESSION_COMPLETED"
    CREDITS_EARNED = "CREDITS_EARNED"
    CREDITS_SPENT = "CREDITS_SPENT"
    NEW_RATING = "NEW_RATING"
