from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.deps import get_current_user
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    AuthResponse,
    GoogleAuthRequest,
    LoginLocalRequest,
    RegisterLocalRequest,
    RegisterLocalResponse,
    UserResponse,
)
from app.modules.auth.services import (
    authenticate_google_user,
    build_auth_response,
    login_local_user,
    register_local_user,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register-local", response_model=RegisterLocalResponse, status_code=status.HTTP_201_CREATED)
def register_local(payload: RegisterLocalRequest, db: Session = Depends(get_db)) -> RegisterLocalResponse:
    try:
        user = register_local_user(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    response = build_auth_response(user, "User registered successfully.")
    return RegisterLocalResponse(**response)


@router.post("/login-local", response_model=AuthResponse)
def login_local(payload: LoginLocalRequest, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        user = login_local_user(db, payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    response = build_auth_response(user, "Logged in successfully.")
    return AuthResponse(**response)


@router.post("/google", response_model=AuthResponse)
def login_with_google(payload: GoogleAuthRequest, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        user, is_new = authenticate_google_user(db, payload.id_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    message = "Registered with Google successfully." if is_new else "Logged in with Google successfully."
    response = build_auth_response(user, message)
    return AuthResponse(**response)


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
