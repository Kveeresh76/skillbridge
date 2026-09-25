"""Shared API test fixtures backed by a throwaway in-memory SQLite database."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 — registers all models on Base.metadata
from app.core.security import hash_password
from app.database.database import Base, get_db
from app.main import app
from app.models import ExchangeRequest, Skill, User, UserSkill
from app.models.common import SkillLevel, UserSkillType


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def exchange(db_session):
    """Two members, one skill each, and a pending request from Ada to Grace."""
    ada = User(full_name="Ada Lovelace", username="ada", email="ada@example.com", hashed_password=hash_password("Secret123!"))
    grace = User(full_name="Grace Hopper", username="grace", email="grace@example.com", hashed_password=hash_password("Secret123!"))
    python = Skill(name="Python", category="Programming")
    design = Skill(name="UI/UX Design", category="Design")
    db_session.add_all([ada, grace, python, design])
    db_session.flush()

    db_session.add_all(
        [
            UserSkill(user_id=ada.id, skill_id=python.id, type=UserSkillType.OFFERED, level=SkillLevel.ADVANCED),
            UserSkill(user_id=grace.id, skill_id=design.id, type=UserSkillType.OFFERED, level=SkillLevel.ADVANCED),
        ]
    )
    request = ExchangeRequest(
        sender_id=ada.id,
        receiver_id=grace.id,
        teaching_skill_id=python.id,
        learning_skill_id=design.id,
        message="I can teach you Python if you teach me design.",
    )
    db_session.add(request)
    db_session.commit()
    return {"ada": ada, "grace": grace, "python": python, "design": design, "request": request}


@pytest.fixture()
def auth_headers(client):
    def _headers(user: User):
        response = client.post("/api/auth/login", json={"email": user.email, "password": "Secret123!"})
        assert response.status_code == 200, response.text
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _headers
