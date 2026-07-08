from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.profile.blocks_v2 import migrate_layout_to_v2, validate_layout_payload
from app.modules.profile.models import UserProfile
from app.modules.profile.schemas import UserProfileUpdateRequest


def get_profile_by_user_id(db: Session, user_id: UUID) -> UserProfile | None:
    return db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))


def get_profile_by_username(db: Session, username: str) -> UserProfile | None:
    return db.scalar(select(UserProfile).where(UserProfile.username == username))


def ensure_profile_layout_v2(profile: UserProfile) -> UserProfile:
    profile.layout_structure = migrate_layout_to_v2(
        profile.layout_structure,
        bio=profile.bio,
        phone=profile.phone,
        zalo=profile.zalo,
        messenger=profile.messenger,
    )
    return profile


def update_profile(
    db: Session,
    profile: UserProfile,
    payload: UserProfileUpdateRequest,
) -> UserProfile:
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)

    if "username" in updates and updates["username"] != profile.username and updates["username"] is not None:
        existing_profile = db.scalar(select(UserProfile).where(UserProfile.username == updates["username"]))
        if existing_profile and existing_profile.user_id != profile.user_id:
            raise ValueError("Username already exists.")

    if "layout_structure" in updates and updates["layout_structure"] is not None:
        updates["layout_structure"] = validate_layout_payload(updates["layout_structure"])

    for field_name, field_value in updates.items():
        setattr(profile, field_name, field_value)

    ensure_profile_layout_v2(profile)

    try:
        db.add(profile)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(profile)
    return profile
