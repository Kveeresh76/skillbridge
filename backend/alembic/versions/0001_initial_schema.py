"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-07

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

skill_level = sa.Enum("BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT", name="skilllevel")
user_skill_type = sa.Enum("OFFERED", "WANTED", name="userskilltype")
transaction_type = sa.Enum("EARNED", "SPENT", "BONUS", "REFUND", "ADJUSTMENT", name="transactiontype")
request_status = sa.Enum("PENDING", "ACCEPTED", "REJECTED", "CANCELLED", "COMPLETED", name="requeststatus")
session_status = sa.Enum("SCHEDULED", "IN_PROGRESS", "COMPLETED", "CANCELLED", name="sessionstatus")
notification_type = sa.Enum(
    "NEW_REQUEST", "REQUEST_ACCEPTED", "REQUEST_REJECTED", "NEW_MESSAGE",
    "SESSION_SCHEDULED", "SESSION_REMINDER", "SESSION_COMPLETED",
    "CREDITS_EARNED", "CREDITS_SPENT", "NEW_RATING",
    name="notificationtype",
)


def upgrade() -> None:
    bind = op.get_bind()
    for enum_type in (skill_level, user_skill_type, transaction_type, request_status, session_status, notification_type):
        enum_type.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("skill_credits", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("skill_credits >= 0", name="ck_users_credits_non_negative"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("bio", sa.Text()),
        sa.Column("location", sa.String(120)),
        sa.Column("timezone", sa.String(64)),
        sa.Column("experience_level", sa.String(32)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False, unique=True),
        sa.Column("category", sa.String(80)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_skills_name", "skills", ["name"])

    op.create_table(
        "user_skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", user_skill_type, nullable=False),
        sa.Column("level", skill_level, nullable=False, server_default="BEGINNER"),
        sa.Column("target_level", skill_level),
        sa.Column("learning_goal", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "skill_id", "type", name="uq_user_skill_type"),
    )

    op.create_table(
        "exchange_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("receiver_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("teaching_skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=False),
        sa.Column("learning_skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=False),
        sa.Column("message", sa.Text()),
        sa.Column("status", request_status, nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("sender_id != receiver_id", name="ck_request_not_self"),
    )

    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "exchange_request_id",
            sa.Integer(),
            sa.ForeignKey("exchange_requests.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("receiver_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("learner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id"), nullable=False),
        sa.Column("exchange_request_id", sa.Integer(), sa.ForeignKey("exchange_requests.id", ondelete="SET NULL")),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("meeting_link", sa.String(500)),
        sa.Column("status", session_status, nullable=False, server_default="SCHEDULED"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("teacher_id != learner_id", name="ck_session_not_self"),
        sa.CheckConstraint("end_time > start_time", name="ck_session_end_after_start"),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewee_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating_range"),
        sa.CheckConstraint("reviewer_id != reviewee_id", name="ck_review_not_self"),
        sa.UniqueConstraint("session_id", "reviewer_id", name="uq_review_per_session_reviewer"),
    )

    op.create_table(
        "credit_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("type", transaction_type, nullable=False),
        sa.Column("description", sa.String(255)),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("sessions.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_credit_transactions_user_id", "credit_transactions", ["user_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", notification_type, nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("body", sa.String(500)),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("related_entity_type", sa.String(50)),
        sa.Column("related_entity_id", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("credit_transactions")
    op.drop_table("reviews")
    op.drop_table("sessions")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("exchange_requests")
    op.drop_table("user_skills")
    op.drop_table("skills")
    op.drop_table("profiles")
    op.drop_table("users")

    bind = op.get_bind()
    for enum_type in (skill_level, user_skill_type, transaction_type, request_status, session_status, notification_type):
        enum_type.drop(bind, checkfirst=True)
