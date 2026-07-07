from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.profile.schemas import UserProfileResponse, UserProfileUpdateRequest
from app.modules.profile.services import get_profile_by_user_id, get_profile_by_username, update_profile


router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/by-user/{user_id}", response_model=UserProfileResponse)
def read_profile_by_user_id(user_id: UUID, db: Session = Depends(get_db)) -> UserProfileResponse:
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    return UserProfileResponse.model_validate(profile)


@router.get("/public/{username}", response_model=UserProfileResponse)
def read_profile_by_username(username: str, db: Session = Depends(get_db)) -> UserProfileResponse:
    profile = get_profile_by_username(db, username)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    return UserProfileResponse.model_validate(profile)


@router.put("/by-user/{user_id}", response_model=UserProfileResponse)
def update_profile_by_user_id(
    user_id: UUID,
    payload: UserProfileUpdateRequest,
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    profile = get_profile_by_user_id(db, user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

    try:
        updated_profile = update_profile(db, profile, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return UserProfileResponse.model_validate(updated_profile)
