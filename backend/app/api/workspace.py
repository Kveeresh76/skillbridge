from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.database import get_db
from app.models import (
    Conversation,
    CreditTransaction,
    ExchangeRequest,
    Message,
    Profile,
    Session as LearningSession,
    User,
    UserSkill,
)
from app.models.common import RequestStatus

router = APIRouter(prefix="/workspace", tags=["workspace"])


class ProfileUpdate(BaseModel):
    bio: str = Field(default="", max_length=1000)
    location: str = Field(default="", max_length=120)
    timezone: str = Field(default="UTC", max_length=64)
    experience_level: str = Field(default="", max_length=32)


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


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
def update_request(request_id: int, status: RequestStatus, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    item = db.get(ExchangeRequest, request_id)
    if not item or item.receiver_id != user.id:
        raise HTTPException(status_code=404, detail="Request not found")
    item.status = status
    db.commit()
    return {"message": "Request updated", "status": status.value}


@router.get("/sessions")
def sessions(user: Annotated[User, Depends(get_current_user)]):
    items = sorted(user.teaching_sessions + user.learning_sessions, key=lambda item: item.start_time)
    return {"sessions": [{"id": item.id, "skill": item.skill.name, "status": item.status.value, "start_time": item.start_time, "end_time": item.end_time, "meeting_link": item.meeting_link, "partner": item.learner.full_name if item.teacher_id == user.id else item.teacher.full_name} for item in items]}


@router.get("/credits")
def credits(user: Annotated[User, Depends(get_current_user)]):
    return {"balance": user.skill_credits, "transactions": [{"id": item.id, "amount": item.amount, "type": item.type.value, "description": item.description, "created_at": item.created_at} for item in sorted(user.transactions, key=lambda item: item.created_at, reverse=True)]}


@router.get("/messages")
def messages(user: Annotated[User, Depends(get_current_user)]):
    conversations = [conversation for conversation in user.sent_requests + user.received_requests if conversation.conversation]
    result = []
    for request in conversations:
        for message in request.conversation.messages:
            if message.sender_id == user.id or message.receiver_id == user.id:
                result.append({"id": message.id, "request_id": request.id, "body": message.body, "sender": message.sender.full_name, "is_read": message.is_read, "created_at": message.created_at})
    return {"messages": sorted(result, key=lambda item: item["created_at"], reverse=True)}


@router.post("/messages/{request_id}")
def send_message(request_id: int, payload: MessageCreate, user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    request = db.get(ExchangeRequest, request_id)
    if not request or user.id not in (request.sender_id, request.receiver_id) or not request.conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    receiver_id = request.receiver_id if request.sender_id == user.id else request.sender_id
    message = Message(conversation_id=request.conversation.id, sender_id=user.id, receiver_id=receiver_id, body=payload.body.strip())
    db.add(message)
    db.commit()
    return {"message": "Message sent", "id": message.id}
