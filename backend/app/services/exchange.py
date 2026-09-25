"""Business logic shared by the exchange-request and messaging endpoints."""
from sqlalchemy.orm import Session as DBSession

from app.models import Conversation, ExchangeRequest, Notification
from app.models.common import NotificationType, RequestStatus

# Who is allowed to move a PENDING request into each terminal status.
TRANSITION_ACTOR = {
    RequestStatus.ACCEPTED: "receiver",
    RequestStatus.REJECTED: "receiver",
    RequestStatus.CANCELLED: "sender",
}


def ensure_conversation(db: DBSession, request: ExchangeRequest) -> Conversation:
    """Return the request's conversation, creating it on first use."""
    if request.conversation:
        return request.conversation
    conversation = Conversation(exchange_request_id=request.id)
    db.add(conversation)
    db.flush()
    return conversation


def notify(
    db: DBSession,
    user_id: int,
    notification_type: NotificationType,
    title: str,
    body: str,
    related_entity_type: str | None = None,
    related_entity_id: int | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        body=body,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
    )
    db.add(notification)
    return notification
