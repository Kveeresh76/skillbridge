from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.common import TimestampMixin


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exchange_request_id: Mapped[int] = mapped_column(
        ForeignKey("exchange_requests.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    exchange_request: Mapped["ExchangeRequest"] = relationship(back_populates="conversation")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at"
    )
