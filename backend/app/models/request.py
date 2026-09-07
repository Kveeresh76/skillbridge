from sqlalchemy import CheckConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.common import RequestStatus, TimestampMixin


class ExchangeRequest(Base, TimestampMixin):
    """
    'I can teach you Python if you teach me React.'
    Sent by one user to another, referencing the skill each side teaches.
    """

    __tablename__ = "exchange_requests"
    __table_args__ = (
        CheckConstraint("sender_id != receiver_id", name="ck_request_not_self"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    teaching_skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)
    learning_skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), nullable=False)

    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[RequestStatus] = mapped_column(
        SAEnum(RequestStatus), nullable=False, default=RequestStatus.PENDING
    )

    sender: Mapped["User"] = relationship(foreign_keys=[sender_id], back_populates="sent_requests")
    receiver: Mapped["User"] = relationship(foreign_keys=[receiver_id], back_populates="received_requests")
    teaching_skill: Mapped["Skill"] = relationship(foreign_keys=[teaching_skill_id])
    learning_skill: Mapped["Skill"] = relationship(foreign_keys=[learning_skill_id])

    conversation: Mapped["Conversation"] = relationship(back_populates="exchange_request", uselist=False)
