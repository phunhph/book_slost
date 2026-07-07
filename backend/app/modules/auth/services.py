from sqlalchemy import select
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.modules.auth.models import User
from app.modules.auth.schemas import RegisterLocalRequest
from app.modules.profile.models import UserProfile


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def register_local_user(db: Session, payload: RegisterLocalRequest) -> User:
    existing_user = db.scalar(select(User).where(User.email == payload.email))
    if existing_user:
        raise ValueError("Email already exists.")

    if payload.username:
        existing_profile = db.scalar(select(UserProfile).where(UserProfile.username == payload.username))
        if existing_profile:
            raise ValueError("Username already exists.")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        auth_provider="local",
        role="customer",
        is_active=True,
    )
    profile = UserProfile(
        user=user,
        username=payload.username,
        display_name=payload.display_name,
    )

    try:
        db.add(user)
        db.add(profile)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(user)
    return user
