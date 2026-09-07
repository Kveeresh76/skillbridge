from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.common import SkillLevel, TimestampMixin, UserSkillType


class Skill(Base, TimestampMixin):
    """The global catalog of skills (e.g. 'Python', 'UI/UX Design')."""

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)

    user_links: Mapped[list["UserSkill"]] = relationship(back_populates="skill")


class UserSkill(Base, TimestampMixin):
    """
    Links a user to a skill either as something they OFFER (can teach) or
    WANT (want to learn). A user may have the same skill in both directions,
    but not twice in the same direction — enforced below.
    """

    __tablename__ = "user_skills"
    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", "type", name="uq_user_skill_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)

    type: Mapped[UserSkillType] = mapped_column(SAEnum(UserSkillType), nullable=False)

    # For OFFERED skills: how well the user can teach it.
    # For WANTED skills: the user's current level.
    level: Mapped[SkillLevel] = mapped_column(SAEnum(SkillLevel), nullable=False, default=SkillLevel.BEGINNER)

    # Only meaningful for WANTED skills — where the learner wants to get to.
    target_level: Mapped[SkillLevel | None] = mapped_column(SAEnum(SkillLevel), nullable=True)
    learning_goal: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(back_populates="user_links")
