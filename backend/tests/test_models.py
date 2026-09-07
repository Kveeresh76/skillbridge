"""
Sanity-checks the ORM models and their relationships using a throwaway
in-memory SQLite database (fast, no Postgres required for this test).
Full constraint behavior (server-side CHECK constraints etc.) is exercised
against real Postgres in the integration tests added in later phases.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.core.security import hash_password
import app.models  # noqa: F401 — registers all models on Base.metadata
from app.models import Skill, User, UserSkill
from app.models.common import SkillLevel, UserSkillType


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_create_user_with_profile_and_skills(db_session):
    user = User(
        full_name="Test User",
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("Secret123!"),
    )
    db_session.add(user)
    db_session.flush()

    python_skill = Skill(name="Python", category="Programming")
    db_session.add(python_skill)
    db_session.flush()

    db_session.add(
        UserSkill(
            user_id=user.id,
            skill_id=python_skill.id,
            type=UserSkillType.OFFERED,
            level=SkillLevel.ADVANCED,
        )
    )
    db_session.commit()

    fetched = db_session.query(User).filter_by(username="testuser").one()
    assert fetched.skill_credits == 0
    assert len(fetched.skills) == 1
    assert fetched.skills[0].skill.name == "Python"


def test_new_user_starts_with_zero_credits(db_session):
    user = User(
        full_name="Zero Credits",
        username="zerocredits",
        email="zero@example.com",
        hashed_password=hash_password("Secret123!"),
    )
    db_session.add(user)
    db_session.commit()
    assert user.skill_credits == 0
