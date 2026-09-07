from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database.database import get_db
from app.models import Skill, User, UserSkill
from app.models.common import UserSkillType

router = APIRouter(prefix="/discover", tags=["discover"])


@router.get("/people")
def discover_people(
    search: str | None = Query(default=None, max_length=80),
    category: str | None = Query(default=None, max_length=80),
    db: Session = Depends(get_db),
):
    links = (
        db.query(UserSkill)
        .join(UserSkill.user)
        .join(UserSkill.skill)
        .options(joinedload(UserSkill.user).joinedload(User.profile), joinedload(UserSkill.skill))
        .filter(UserSkill.type == UserSkillType.OFFERED)
        .order_by(User.full_name.asc(), Skill.name.asc())
        .all()
    )

    profiles = {}
    for link in links:
        user = link.user
        skill = link.skill
        if search and search.lower() not in skill.name.lower() and search.lower() not in user.full_name.lower():
            continue
        if category and skill.category != category:
            continue

        entry = profiles.setdefault(
            user.id,
            {
                "id": user.id,
                "full_name": user.full_name,
                "username": user.username,
                "bio": user.profile.bio if user.profile else None,
                "location": user.profile.location if user.profile else None,
                "experience_level": user.profile.experience_level if user.profile else None,
                "offered_skills": [],
                "wanted_skills": [
                    wanted.skill.name
                    for wanted in user.skills
                    if wanted.type == UserSkillType.WANTED
                ],
            },
        )
        entry["offered_skills"].append(
            {"name": skill.name, "category": skill.category, "level": link.level.value}
        )

    return {"people": list(profiles.values())}


@router.get("/categories")
def discover_categories(db: Session = Depends(get_db)):
    categories = (
        db.query(Skill.category)
        .filter(Skill.category.is_not(None))
        .distinct()
        .order_by(Skill.category.asc())
        .all()
    )
    return {"categories": [category for (category,) in categories]}


@router.get("/skills")
def discover_skills(db: Session = Depends(get_db)):
    skills = db.query(Skill).order_by(Skill.category.asc(), Skill.name.asc()).all()
    return {"skills": [{"id": skill.id, "name": skill.name, "category": skill.category} for skill in skills]}
