import bcrypt
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token
from app.modules.auth.models import User
from app.modules.auth.schemas import RegisterLocalRequest
from app.modules.profile.models import UserProfile


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain_password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode(), password_hash.encode())
    except ValueError:
        return False


def build_auth_response(user: User, message: str) -> dict:
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": user,
        "message": message,
    }


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


def login_local_user(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        raise ValueError("Invalid email or password.")

    if not user.is_active:
        raise ValueError("Account is inactive.")

    if not verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password.")

    return user


def authenticate_google_user(db: Session, token: str) -> tuple[User, bool]:
    settings = get_settings()
    if not settings.google_client_id:
        raise ValueError("Google login is not configured on the server.")

    try:
        id_info = google_id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError as exc:
        raise ValueError("Invalid Google token.") from exc

    email = id_info.get("email")
    if not email:
        raise ValueError("Google account does not provide an email.")

    if not id_info.get("email_verified", False):
        raise ValueError("Google email is not verified.")

    existing_user = db.scalar(select(User).where(User.email == email))
    if existing_user:
        if not existing_user.is_active:
            raise ValueError("Account is inactive.")
        return existing_user, False

    display_name = id_info.get("name")
    user = User(
        email=email,
        password_hash=None,
        auth_provider="google",
        role="customer",
        is_active=True,
    )
    profile = UserProfile(
        user=user,
        display_name=display_name,
    )

    try:
        db.add(user)
        db.add(profile)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(user)
    return user, True
