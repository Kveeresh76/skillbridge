from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.common import TimestampMixin, TransactionType


class CreditTransaction(Base, TimestampMixin):
    """
    An append-only ledger entry. A user's `skill_credits` balance must never
    change without a matching row here — see services/credit_service.py,
    which writes both inside a single DB transaction.
    """

    __tablename__ = "credit_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # positive or negative
    type: Mapped[TransactionType] = mapped_column(SAEnum(TransactionType), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True
    )

    user: Mapped["User"] = relationship(back_populates="transactions")
    session: Mapped["Session"] = relationship(back_populates="transactions")
