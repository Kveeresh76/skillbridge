"""
Development seed data for SkillBridge.

Populates the database with a believable, internally-consistent demo
dataset: users, skills, exchange requests, conversations + messages,
sessions, reviews, credit transactions, and notifications.

This is SEED DATA for local development only — never run against a
production database. Usernames are prefixed nowhere specially, but every
user's password is the fixed demo password below, which only makes sense
in a dev environment.

Usage:
    python -m app.seed
"""
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session as DBSession

from app.core.security import hash_password
from app.database.database import Base, SessionLocal, engine
from app.models import (
    Conversation,
    CreditTransaction,
    ExchangeRequest,
    Message,
    Notification,
    Profile,
    Review,
    Skill,
    Session,
    User,
    UserSkill,
)
from app.models.common import (
    NotificationType,
    RequestStatus,
    SessionStatus,
    SkillLevel,
    TransactionType,
    UserSkillType,
)

DEMO_PASSWORD = "SkillBridge!2026"  # dev-only fixed password for every seeded user
random.seed(42)

SKILL_CATALOG = [
    ("Python", "Programming"),
    ("JavaScript", "Programming"),
    ("React", "Programming"),
    ("Java", "Programming"),
    ("SQL", "Data"),
    ("Data Structures", "Computer Science"),
    ("Machine Learning", "Data"),
    ("Data Visualization", "Data"),
    ("UI/UX Design", "Design"),
    ("Graphic Design", "Design"),
    ("Photography", "Creative"),
    ("Video Editing", "Creative"),
    ("Public Speaking", "Soft Skills"),
    ("English", "Language"),
    ("Telugu", "Language"),
    ("Spanish", "Language"),
    ("Guitar", "Music"),
    ("Piano", "Music"),
    ("Yoga", "Wellness"),
    ("Cooking", "Lifestyle"),
    ("Excel", "Productivity"),
    ("Docker", "DevOps"),
    ("Git & GitHub", "DevOps"),
    ("Creative Writing", "Writing"),
]

USER_SEED = [
    ("Veeresh Kumar", "veeresh", "veeresh@example.com", "Hyderabad, India"),
    ("Ananya Rao", "ananya_r", "ananya@example.com", "Bengaluru, India"),
    ("Rahul Mehta", "rahulm", "rahul@example.com", "Pune, India"),
    ("Priya Nair", "priyan", "priya@example.com", "Kochi, India"),
    ("Arjun Reddy", "arjun_reddy", "arjun@example.com", "Hyderabad, India"),
    ("Sneha Iyer", "sneha_i", "sneha@example.com", "Chennai, India"),
    ("Kabir Singh", "kabirs", "kabir@example.com", "Delhi, India"),
    ("Meera Pillai", "meerap", "meera@example.com", "Kochi, India"),
    ("Aditya Verma", "adityav", "aditya@example.com", "Mumbai, India"),
    ("Divya Krishnan", "divyak", "divya@example.com", "Chennai, India"),
    ("Rohan Das", "rohand", "rohan@example.com", "Kolkata, India"),
    ("Neha Joshi", "nehaj", "neha@example.com", "Pune, India"),
    ("Farhan Ali", "farhana", "farhan@example.com", "Hyderabad, India"),
    ("Kavya Menon", "kavyam", "kavya@example.com", "Bengaluru, India"),
    ("Yusuf Khan", "yusufk", "yusuf@example.com", "Lucknow, India"),
]

BIOS = [
    "Building things and figuring out the rest along the way.",
    "Believer in learning by teaching.",
    "Here to trade skills, not tuition.",
    "Always got a side project brewing.",
    "Curious generalist, deep diver when it counts.",
]

EXPERIENCE_LEVELS = ["Student", "Early Career", "Mid Career", "Senior"]


def _now():
    return datetime.now(timezone.utc)


def clear_all(db: DBSession):
    """Delete in FK-safe order so re-running the seed script is idempotent."""
    for model in [
        Notification,
        CreditTransaction,
        Review,
        Session,
        Message,
        Conversation,
        ExchangeRequest,
        UserSkill,
        Profile,
        User,
        Skill,
    ]:
        db.query(model).delete()
    db.commit()


def record_transaction(db: DBSession, user: User, amount: int, ttype: TransactionType, description: str, session=None):
    """
    The one place seed data touches a balance — mirrors what
    services/credit_service.py will do in Phase 9: a transaction row and
    the denormalized balance change together, and the balance never goes
    negative.
    """
    new_balance = user.skill_credits + amount
    if new_balance < 0:
        raise ValueError(f"Refusing to seed a negative balance for {user.username}")
    user.skill_credits = new_balance
    db.add(
        CreditTransaction(
            user_id=user.id,
            amount=amount,
            type=ttype,
            description=description,
            session_id=session.id if session else None,
        )
    )


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        clear_all(db)

        # --- Skills catalog ---
        skills = {}
        for name, category in SKILL_CATALOG:
            skill = Skill(name=name, category=category)
            db.add(skill)
            skills[name] = skill
        db.flush()

        # --- Users + profiles ---
        users = []
        for i, (full_name, username, email, location) in enumerate(USER_SEED):
            user = User(
                full_name=full_name,
                username=username,
                email=email,
                hashed_password=hash_password(DEMO_PASSWORD),
                skill_credits=1,
                is_active=True,
            )
            db.add(user)
            db.flush()
            db.add(
                Profile(
                    user_id=user.id,
                    bio=BIOS[i % len(BIOS)],
                    location=location,
                    timezone="Asia/Kolkata",
                    experience_level=EXPERIENCE_LEVELS[i % len(EXPERIENCE_LEVELS)],
                )
            )
            users.append(user)
        db.flush()

        # --- Skills offered / wanted per user ---
        skill_names = list(skills.keys())
        for user in users:
            offered = random.sample(skill_names, k=random.randint(2, 4))
            remaining = [s for s in skill_names if s not in offered]
            wanted = random.sample(remaining, k=random.randint(2, 3))

            for name in offered:
                db.add(
                    UserSkill(
                        user_id=user.id,
                        skill_id=skills[name].id,
                        type=UserSkillType.OFFERED,
                        level=random.choice(list(SkillLevel)),
                    )
                )
            for name in wanted:
                db.add(
                    UserSkill(
                        user_id=user.id,
                        skill_id=skills[name].id,
                        type=UserSkillType.WANTED,
                        level=SkillLevel.BEGINNER,
                        target_level=random.choice([SkillLevel.INTERMEDIATE, SkillLevel.ADVANCED]),
                        learning_goal=f"Get comfortable enough with {name} to use it on real projects.",
                    )
                )
        db.flush()

        # --- Exchange requests (mix of statuses) ---
        requests = []
        request_specs = [
            (0, 1, "Python", "React", RequestStatus.ACCEPTED),
            (1, 0, "React", "Python", RequestStatus.PENDING),
            (2, 3, "SQL", "UI/UX Design", RequestStatus.ACCEPTED),
            (4, 5, "Machine Learning", "Photography", RequestStatus.COMPLETED),
            (6, 7, "Guitar", "Public Speaking", RequestStatus.REJECTED),
            (8, 9, "Docker", "Video Editing", RequestStatus.ACCEPTED),
            (10, 11, "Excel", "Creative Writing", RequestStatus.PENDING),
            (12, 13, "English", "Cooking", RequestStatus.CANCELLED),
        ]
        for sender_idx, receiver_idx, teach_name, learn_name, status in request_specs:
            sender, receiver = users[sender_idx], users[receiver_idx]
            req = ExchangeRequest(
                sender_id=sender.id,
                receiver_id=receiver.id,
                teaching_skill_id=skills[teach_name].id,
                learning_skill_id=skills[learn_name].id,
                message=f"I can teach you {teach_name} if you teach me {learn_name}.",
                status=status,
            )
            db.add(req)
            db.flush()
            requests.append(req)

        # --- Conversations + messages for accepted/completed requests ---
        chat_starters = [
            "Hey! Excited to get started — when works for you?",
            "How about this weekend for our first session?",
            "Sounds good. I'll send over a meeting link.",
            "Looking forward to it!",
        ]
        conversations = {}
        for req in requests:
            if req.status in (RequestStatus.ACCEPTED, RequestStatus.COMPLETED):
                convo = Conversation(exchange_request_id=req.id)
                db.add(convo)
                db.flush()
                conversations[req.id] = convo
                base_time = _now() - timedelta(days=5)
                for i, text in enumerate(chat_starters):
                    sender, receiver = (req.sender, req.receiver) if i % 2 == 0 else (req.receiver, req.sender)
                    db.add(
                        Message(
                            conversation_id=convo.id,
                            sender_id=sender.id,
                            receiver_id=receiver.id,
                            body=text,
                            is_read=i < len(chat_starters) - 1,
                            created_at=base_time + timedelta(hours=i),
                        )
                    )
        db.flush()

        # --- Sessions (scheduled + completed) tied to accepted/completed requests ---
        sessions = []
        for req in requests:
            if req.status not in (RequestStatus.ACCEPTED, RequestStatus.COMPLETED):
                continue
            is_completed = req.status == RequestStatus.COMPLETED
            start = _now() + (timedelta(days=3) if not is_completed else -timedelta(days=7))
            sess = Session(
                teacher_id=req.sender_id,
                learner_id=req.receiver_id,
                skill_id=req.teaching_skill_id,
                exchange_request_id=req.id,
                start_time=start,
                end_time=start + timedelta(hours=1),
                meeting_link="https://meet.skillbridge.dev/demo-room",
                status=SessionStatus.COMPLETED if is_completed else SessionStatus.SCHEDULED,
            )
            db.add(sess)
            db.flush()
            sessions.append(sess)

            if is_completed:
                teacher, learner = req.sender, req.receiver
                record_transaction(db, teacher, +1, TransactionType.EARNED, f"Taught {req.teaching_skill.name}", sess)
                record_transaction(db, learner, -1, TransactionType.SPENT, f"Learned {req.teaching_skill.name}", sess)

                db.add(
                    Review(
                        session_id=sess.id,
                        reviewer_id=learner.id,
                        reviewee_id=teacher.id,
                        rating=5,
                        comment=f"Great {req.teaching_skill.name} session, clear and patient explanations.",
                    )
                )
                db.add(
                    Notification(
                        user_id=teacher.id,
                        type=NotificationType.NEW_RATING,
                        title="You got a new rating",
                        body=f"{learner.full_name} left you a 5-star review.",
                    )
                )

        # --- A few bonus/adjustment transactions to show the ledger's range ---
        record_transaction(db, users[0], +2, TransactionType.BONUS, "Welcome bonus for completing your profile")
        record_transaction(db, users[3], +1, TransactionType.ADJUSTMENT, "Manual credit correction by support")

        # --- Notifications for pending/accepted requests ---
        for req in requests:
            if req.status == RequestStatus.PENDING:
                db.add(
                    Notification(
                        user_id=req.receiver_id,
                        type=NotificationType.NEW_REQUEST,
                        title="New exchange request",
                        body=f"{req.sender.full_name} wants to trade {req.teaching_skill.name} for {req.learning_skill.name}.",
                    )
                )
            elif req.status == RequestStatus.ACCEPTED:
                db.add(
                    Notification(
                        user_id=req.sender_id,
                        type=NotificationType.REQUEST_ACCEPTED,
                        title="Request accepted",
                        body=f"{req.receiver.full_name} accepted your exchange request.",
                    )
                )

        db.commit()

        print(f"Seeded {len(users)} users, {len(skills)} skills, {len(requests)} requests, "
              f"{len(sessions)} sessions.")
        print(f"Every seeded user's password is: {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
