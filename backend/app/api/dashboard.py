from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.database import get_db
from app.models import Message, Session as LearningSession, User
from app.models.common import SessionStatus

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    now = datetime.now(timezone.utc)
    upcoming_query = (
        db.query(LearningSession)
        .filter(
            or_(LearningSession.teacher_id == user.id, LearningSession.learner_id == user.id),
            LearningSession.status == SessionStatus.SCHEDULED,
            LearningSession.start_time >= now,
        )
        .order_by(LearningSession.start_time.asc())
    )
    upcoming = upcoming_query.first()

    unread_messages = (
        db.query(func.count(Message.id))
        .filter(Message.receiver_id == user.id, Message.is_read.is_(False))
        .scalar()
        or 0
    )

    result = {
        "skill_credits": user.skill_credits,
        "upcoming_sessions": upcoming_query.count(),
        "unread_messages": unread_messages,
        "pending_requests": len([request for request in user.received_requests if request.status.value == "PENDING"]),
        "next_session": None,
    }

    if upcoming:
        partner = upcoming.learner if upcoming.teacher_id == user.id else upcoming.teacher
        result["next_session"] = {
            "id": upcoming.id,
            "skill": upcoming.skill.name,
            "start_time": upcoming.start_time,
            "meeting_link": upcoming.meeting_link,
            "partner_name": partner.full_name,
        }

    return result
