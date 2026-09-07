from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.database import get_db
from app.models import ExchangeRequest, Skill, User, UserSkill
from app.models.common import UserSkillType

router = APIRouter(prefix="/requests", tags=["requests"])


class ExchangeRequestCreate(BaseModel):
    receiver_id: int
    teaching_skill_id: int
    learning_skill_id: int
    message: str = Field(min_length=1, max_length=500)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_exchange_request(
    payload: ExchangeRequestCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if payload.receiver_id == user.id:
        raise HTTPException(status_code=400, detail="You cannot send an exchange request to yourself")

    receiver = db.get(User, payload.receiver_id)
    teaching_skill = db.get(Skill, payload.teaching_skill_id)
    learning_skill = db.get(Skill, payload.learning_skill_id)
    if not receiver or not receiver.is_active:
        raise HTTPException(status_code=404, detail="That member is no longer available")
    if not teaching_skill or not learning_skill:
        raise HTTPException(status_code=404, detail="Select valid skills for the exchange")

    offers_skill = (
        db.query(UserSkill)
        .filter(
            UserSkill.user_id == user.id,
            UserSkill.skill_id == teaching_skill.id,
            UserSkill.type == UserSkillType.OFFERED,
        )
        .first()
    )
    if not offers_skill:
        raise HTTPException(status_code=400, detail="You can only offer a skill listed in your profile")

    duplicate = (
        db.query(ExchangeRequest)
        .filter(
            ExchangeRequest.sender_id == user.id,
            ExchangeRequest.receiver_id == receiver.id,
            ExchangeRequest.teaching_skill_id == teaching_skill.id,
            ExchangeRequest.learning_skill_id == learning_skill.id,
            ExchangeRequest.status == "PENDING",
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="You already sent this exchange request")

    exchange_request = ExchangeRequest(
        sender_id=user.id,
        receiver_id=receiver.id,
        teaching_skill_id=teaching_skill.id,
        learning_skill_id=learning_skill.id,
        message=payload.message.strip(),
    )
    db.add(exchange_request)
    db.commit()
    db.refresh(exchange_request)

    return {"id": exchange_request.id, "status": exchange_request.status.value, "message": "Exchange request sent"}
