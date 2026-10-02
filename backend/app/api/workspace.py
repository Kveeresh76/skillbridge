from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.database import get_db
from app.models import (
    Conversation,
    ExchangeRequest,
    Message,
    Notification,
    Profile,
    User,
)
from app.models.common import NotificationType, RequestStatus
from app.services.exchange import TRANSITION_ACTOR, ensure_conversation, notify

router = APIRouter(prefix="/workspace", tags=["workspace"])


class ProfileUpdate(BaseModel):
    bio: str = Field(default="", max_length=1000)
    location: str = Field(default="", max_length=120)
    timezone: str = Field(default="UTC", max_length=64)
    experience_level: str = Field(default="", max_length=32)


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class RequestStatusUpdate(BaseModel):
    status: RequestStatus


def request_json(item: ExchangeRequest):
    return {"id": item.id, "status": item.status.value, "message": item.message, "sender": item.sender.full_name, "receiver": item.receiver.full_name, "teaching_skill": item.teaching_skill.name, "learning_skill": item.learning_skill.name, "created_at": item.created_at}


@router.get("/profile")
def profile(user: Annotated[User, Depends(get_current_user)]):
    return {"user": {"id": user.id, "full_name": user.full_name, "username": user.username, "email": user.email, "skill_credits": user.skill_credits}, "profile": {"bio": user.profile.bio if user.profile else "", "location": user.profile.location if user.profile else "", "timezone": user.profile.timezone if user.profile else "UTC", "experience_level": user.profile.experience_level if user.profile else ""}, "skills": [{"id": link.skill.id, "name": link.skill.name, "type": link.type.value, "level": link.level.value} for link in user.skills]}


@router.put("/profile")
def update_profile(payload: ProfileUpdate, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    profile = user.profile or Profile(user_id=user.id)
    profile.bio = payload.bio
    profile.location = payload.location
    profile.timezone = payload.timezone
    profile.experience_level = payload.experience_level
    db.add(profile)
    db.commit()
    return {"message": "Profile updated"}


@router.get("/requests")
def requests(user: Annotated[User, Depends(get_current_user)]):
    return {"incoming": [request_json(item) for item in user.received_requests], "outgoing": [request_json(item) for item in user.sent_requests]}


@router.patch("/requests/{request_id}")
def update_request(
    request_id: int,
    payload: RequestStatusUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    item = db.get(ExchangeRequest, request_id)
    if not item or user.id not in (item.sender_id, item.receiver_id):
        raise HTTPException(status_code=404, detail="Request not found")

    actor = "receiver" if item.receiver_id == user.id else "sender"
    if TRANSITION_ACTOR.get(payload.status) != actor:
        raise HTTPException(status_code=403, detail=f"You cannot mark this request as {payload.status.value.lower()}")
    if item.status != RequestStatus.PENDING:
        raise HTTPException(status_code=409, detail=f"This request was already {item.status.value.lower()}")

    item.status = payload.status
    if payload.status == RequestStatus.ACCEPTED:
        ensure_conversation(db, item)
        notify(
            db,
            item.sender_id,
            NotificationType.REQUEST_ACCEPTED,
            "Request accepted",
            f"{user.full_name} accepted your exchange request. Your conversation is open.",
            "exchange_request",
            item.id,
        )
    elif payload.status == RequestStatus.REJECTED:
        notify(
            db,
            item.sender_id,
            NotificationType.REQUEST_REJECTED,
            "Request declined",
            f"{user.full_name} declined your exchange request.",
            "exchange_request",
            item.id,
        )

    db.commit()
    return {"message": "Request updated", "status": item.status.value}


@router.get("/sessions")
def sessions(user: Annotated[User, Depends(get_current_user)]):
    items = sorted(user.teaching_sessions + user.learning_sessions, key=lambda item: item.start_time)
    return {"sessions": [{"id": item.id, "skill": item.skill.name, "status": item.status.value, "start_time": item.start_time, "end_time": item.end_time, "meeting_link": item.meeting_link, "partner": item.learner.full_name if item.teacher_id == user.id else item.teacher.full_name} for item in items]}


@router.get("/credits")
def credits(user: Annotated[User, Depends(get_current_user)]):
    return {"balance": user.skill_credits, "transactions": [{"id": item.id, "amount": item.amount, "type": item.type.value, "description": item.description, "created_at": item.created_at} for item in sorted(user.transactions, key=lambda item: item.created_at, reverse=True)]}


def thread_json(user: User, request: ExchangeRequest, conversation: Conversation):
    messages = [
        {
            "id": message.id,
            "body": message.body,
            "sender": message.sender.full_name,
            "is_mine": message.sender_id == user.id,
            "is_read": message.is_read,
            "created_at": message.created_at,
        }
        for message in conversation.messages
    ]
    partner = request.receiver if request.sender_id == user.id else request.sender
    return {
        "request_id": request.id,
        "partner": partner.full_name,
        "teaching_skill": request.teaching_skill.name,
        "learning_skill": request.learning_skill.name,
        "unread": sum(1 for message in conversation.messages if message.receiver_id == user.id and not message.is_read),
        "last_activity": messages[-1]["created_at"] if messages else request.created_at,
        "messages": messages,
    }


@router.get("/messages")
def messages(user: Annotated[User, Depends(get_current_user)]):
    """Conversations the user takes part in, newest activity first."""
    threads = [
        thread_json(user, request, request.conversation)
        for request in user.sent_requests + user.received_requests
        if request.conversation
    ]
    return {"threads": sorted(threads, key=lambda thread: thread["last_activity"], reverse=True)}


def get_participating_request(db: Session, request_id: int, user: User) -> ExchangeRequest:
    request = db.get(ExchangeRequest, request_id)
    if not request or user.id not in (request.sender_id, request.receiver_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return request


@router.post("/messages/{request_id}")
def send_message(request_id: int, payload: MessageCreate, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    request = get_participating_request(db, request_id, user)
    if request.status not in (RequestStatus.ACCEPTED, RequestStatus.COMPLETED):
        raise HTTPException(status_code=409, detail="You can only message once the exchange request is accepted")

    conversation = ensure_conversation(db, request)
    receiver_id = request.receiver_id if request.sender_id == user.id else request.sender_id
    message = Message(conversation_id=conversation.id, sender_id=user.id, receiver_id=receiver_id, body=payload.body.strip())
    db.add(message)
    notify(
        db,
        receiver_id,
        NotificationType.NEW_MESSAGE,
        "New message",
        f"{user.full_name} sent you a message.",
        "exchange_request",
        request.id,
    )
    db.commit()
    return {"message": "Message sent", "id": message.id}


@router.post("/messages/{request_id}/read")
def mark_thread_read(request_id: int, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    request = get_participating_request(db, request_id, user)
    unread = [
        message
        for message in (request.conversation.messages if request.conversation else [])
        if message.receiver_id == user.id and not message.is_read
    ]
    for message in unread:
        message.is_read = True
    db.commit()
    return {"message": "Thread marked as read", "marked_read": len(unread)}


@router.get("/notifications")
def notifications(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    items = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .limit(20)
        .all()
    )
    return {
        "unread": sum(1 for item in items if not item.is_read),
        "notifications": [
            {
                "id": item.id,
                "type": item.type.value,
                "title": item.title,
                "body": item.body,
                "is_read": item.is_read,
                "created_at": item.created_at,
            }
            for item in items
        ],
    }


@router.post("/notifications/read")
def mark_notifications_read(user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    marked = (
        db.query(Notification)
        .filter(Notification.user_id == user.id, Notification.is_read.is_(False))
        .update({Notification.is_read: True}, synchronize_session=False)
    )
    db.commit()
    return {"message": "Notifications marked as read", "marked_read": marked}
