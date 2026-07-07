from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.schemas import RegisterLocalRequest, RegisterLocalResponse, UserResponse
from app.modules.auth.services import register_local_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register-local", response_model=RegisterLocalResponse, status_code=status.HTTP_201_CREATED)
def register_local(payload: RegisterLocalRequest, db: Session = Depends(get_db)) -> RegisterLocalResponse:
    try:
        user = register_local_user(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return RegisterLocalResponse(user=UserResponse.model_validate(user))
