from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from app.core.config import get_settings


def resolve_token_ttl_minutes(role: str | None) -> int:
    settings = get_settings()
    normalized = (role or "").strip().lower()
    if normalized in {"admin", "kol"}:
        return settings.jwt_workspace_expire_minutes
    # customer and any unknown role fall back to short client TTL
    return settings.jwt_client_expire_minutes


def create_access_token(user_id: UUID, role: str | None = None) -> tuple[str, int, datetime]:
    """Return (token, expires_in_seconds, expires_at_utc)."""
    settings = get_settings()
    ttl_minutes = resolve_token_ttl_minutes(role)
    expire = datetime.now(UTC) + timedelta(minutes=ttl_minutes)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, ttl_minutes * 60, expire


def decode_access_token(token: str) -> UUID | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None

    subject = payload.get("sub")
    if not subject:
        return None

    try:
        return UUID(str(subject))
    except ValueError:
        return None
