from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.deps import get_current_user
from app.modules.auth.models import User
from app.modules.profile.schemas import UserProfileResponse, UserProfileUpdateRequest, SocialPlatformResponse
from app.modules.profile.services import (
    ensure_profile_layout_v2,
    get_profile_by_user_id,
    get_profile_by_username,
    update_profile,
)


router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/by-user/{user_id}", response_model=UserProfileResponse)
def read_profile_by_user_id(user_id: UUID, db: Session = Depends(get_db)) -> UserProfileResponse:
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    profile = ensure_profile_layout_v2(profile)
    return UserProfileResponse.model_validate(profile)


@router.get("/public/{username}", response_model=UserProfileResponse)
def read_profile_by_username(username: str, db: Session = Depends(get_db)) -> UserProfileResponse:
    profile = get_profile_by_username(db, username)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    profile = ensure_profile_layout_v2(profile)
    return UserProfileResponse.model_validate(profile)


@router.put("/by-user/{user_id}", response_model=UserProfileResponse)
def update_profile_by_user_id(
    user_id: UUID,
    payload: UserProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserProfileResponse:
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own profile.")
    if current_user.role not in {"kol", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only KOL accounts can customize public profiles.")

    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    try:
        updated_profile = update_profile(db, profile, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return UserProfileResponse.model_validate(ensure_profile_layout_v2(updated_profile))


@router.get("/platforms", response_model=list[SocialPlatformResponse])
def get_active_platforms(db: Session = Depends(get_db)) -> list[SocialPlatformResponse]:
    from app.modules.profile.models import SocialPlatform
    from sqlalchemy import select
    stmt = select(SocialPlatform).where(SocialPlatform.is_active == True).order_by(SocialPlatform.label.asc())
    platforms = db.scalars(stmt).all()
    return platforms
