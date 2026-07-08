from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.modules.auth.deps import get_optional_user
from app.modules.auth.models import User
from app.modules.auth.role_deps import require_admin, require_kol
from app.modules.auth.schemas import UserResponse
from app.modules.booking.models import Booking
from app.modules.booking.schemas import (
    BookingCreateRequest,
    BookingResponse,
    BookingStatusUpdateRequest,
    KolPublicCard,
)
from app.modules.booking.services import (
    create_booking,
    get_booking_detail,
    get_dashboard_stats,
    get_kol_dashboard_stats,
    list_bookings_for_admin,
    list_bookings_for_kol,
    list_public_kols,
    update_booking_status,
)
from app.modules.profile.models import UserProfile


router = APIRouter(tags=["bookings"])


@router.get("/public/kols", response_model=list[KolPublicCard])
def get_public_kols(db: Session = Depends(get_db)) -> list[KolPublicCard]:
    return list_public_kols(db)


@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking_endpoint(
    payload: BookingCreateRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> BookingResponse:
    try:
        booking = create_booking(db, payload, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    detail = get_booking_detail(db, booking.id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to load booking.")
    return BookingResponse.model_validate(detail)


admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.get("/dashboard")
def admin_dashboard(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, int]:
    return get_dashboard_stats(db)


@admin_router.get("/users", response_model=list[UserResponse])
def admin_list_users(
    role: str | None = None,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    stmt = select(User).order_by(User.created_at.desc())
    if role:
        stmt = stmt.where(User.role == role)
    users = db.scalars(stmt).all()
    return [UserResponse.model_validate(user) for user in users]


@admin_router.get("/kols")
def admin_list_kols(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[dict]:
    rows = db.execute(
        select(User, UserProfile)
        .join(UserProfile, UserProfile.user_id == User.id, isouter=True)
        .where(User.role == "kol")
        .order_by(User.created_at.desc())
    ).all()
    return [
        {
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
            "username": profile.username if profile else None,
            "display_name": profile.display_name if profile else None,
            "created_at": user.created_at.isoformat(),
        }
        for user, profile in rows
    ]


@admin_router.get("/customers")
def admin_list_customers(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[dict]:
    rows = db.execute(
        select(User, UserProfile)
        .join(UserProfile, UserProfile.user_id == User.id, isouter=True)
        .where(User.role == "customer")
        .order_by(User.created_at.desc())
    ).all()
    return [
        {
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
            "display_name": profile.display_name if profile else None,
            "phone": profile.phone if profile else None,
            "created_at": user.created_at.isoformat(),
        }
        for user, profile in rows
    ]


@admin_router.get("/bookings", response_model=list[BookingResponse])
def admin_list_bookings(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[BookingResponse]:
    return [BookingResponse.model_validate(item) for item in list_bookings_for_admin(db)]


kol_router = APIRouter(prefix="/kol", tags=["kol"])


@kol_router.get("/dashboard")
def kol_dashboard(current_user: User = Depends(require_kol), db: Session = Depends(get_db)) -> dict[str, int]:
    if current_user.role != "kol":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="KOL account required.")
    return get_kol_dashboard_stats(db, current_user.id)


@kol_router.get("/bookings", response_model=list[BookingResponse])
def kol_list_bookings(current_user: User = Depends(require_kol), db: Session = Depends(get_db)) -> list[BookingResponse]:
    if current_user.role != "kol":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="KOL account required.")
    return [BookingResponse.model_validate(item) for item in list_bookings_for_kol(db, current_user.id)]


@kol_router.patch("/bookings/{booking_id}", response_model=BookingResponse)
def kol_update_booking_status(
    booking_id: UUID,
    payload: BookingStatusUpdateRequest,
    current_user: User = Depends(require_kol),
    db: Session = Depends(get_db),
) -> BookingResponse:
    if current_user.role != "kol":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="KOL account required.")
    try:
        update_booking_status(db, booking_id, payload.status, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    detail = get_booking_detail(db, booking_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")
    return BookingResponse.model_validate(detail)
