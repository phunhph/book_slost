from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.modules.auth.services import authenticate_google_user, build_auth_response


router = APIRouter(tags=["oauth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


def create_oauth_state(app_target: str) -> str:
    settings = get_settings()
    payload = {
        "app": app_target,
        "exp": datetime.now(UTC) + timedelta(minutes=10),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_oauth_state(state: str) -> str:
    settings = get_settings()
    try:
        payload = jwt.decode(state, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise ValueError("Invalid OAuth state.") from exc

    app_target = payload.get("app")
    if app_target not in {"admin", "client", "kol"}:
        raise ValueError("Invalid OAuth state.")
    return app_target


def redirect_with_error(app_target: str, message: str) -> RedirectResponse:
    settings = get_settings()
    callback_url = settings.frontend_callback_url(app_target)
    query = urlencode({"error": message})
    return RedirectResponse(f"{callback_url}?{query}", status_code=status.HTTP_302_FOUND)


@router.get("/auth/google")
def start_google_oauth(app: str = Query("admin", pattern="^(admin|client|kol)$")) -> RedirectResponse:
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured on the server.",
        )

    state = create_oauth_state(app)
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{urlencode(params)}", status_code=status.HTTP_302_FOUND)


@router.get("/auth/callback")
def google_oauth_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    settings = get_settings()
    app_target = "admin"

    if state:
        try:
            app_target = decode_oauth_state(state)
        except ValueError:
            return redirect_with_error("admin", "Phien dang nhap Google khong hop le.")

    if error:
        return redirect_with_error(app_target, "Ban da huy dang nhap Google.")

    if not code or not state:
        return redirect_with_error(app_target, "Thieu ma xac thuc tu Google.")

    try:
        with httpx.Client(timeout=10.0) as client:
            token_response = client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
    except httpx.HTTPError:
        return redirect_with_error(app_target, "Khong the ket noi den Google.")

    if token_response.status_code != status.HTTP_200_OK:
        return redirect_with_error(app_target, "Google tu choi ma xac thuc.")

    token_data = token_response.json()
    id_token = token_data.get("id_token")
    if not id_token:
        return redirect_with_error(app_target, "Google khong tra ve id token.")

    try:
        user, _ = authenticate_google_user(db, id_token)
    except ValueError as exc:
        return redirect_with_error(app_target, str(exc))

    access_token, _expires_in, _expires_at = create_access_token(user.id, user.role)
    callback_url = settings.frontend_callback_url(app_target)
    query = urlencode({"access_token": access_token})
    return RedirectResponse(f"{callback_url}?{query}", status_code=status.HTTP_302_FOUND)
