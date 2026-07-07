from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.profile.models import UserProfile
from app.modules.profile.schemas import LayoutBlock, UserProfileUpdateRequest


def get_profile_by_user_id(db: Session, user_id: UUID) -> UserProfile | None:
    return db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))


def get_profile_by_username(db: Session, username: str) -> UserProfile | None:
    return db.scalar(select(UserProfile).where(UserProfile.username == username))


def update_profile(
    db: Session,
    profile: UserProfile,
    payload: UserProfileUpdateRequest,
) -> UserProfile:
    updates = payload.model_dump(exclude_unset=True)

    if "username" in updates and updates["username"] != profile.username and updates["username"] is not None:
        existing_profile = db.scalar(select(UserProfile).where(UserProfile.username == updates["username"]))
        if existing_profile and existing_profile.user_id != profile.user_id:
            raise ValueError("Username already exists.")

    if "layout_structure" in updates and updates["layout_structure"] is not None:
        updates["layout_structure"] = [block.model_dump() if isinstance(block, LayoutBlock) else block for block in updates["layout_structure"]]

    for field_name, field_value in updates.items():
        setattr(profile, field_name, field_value)

    try:
        db.add(profile)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(profile)
    return profile
