from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.uploads import save_payment_proof
from app.modules.auth.deps import get_optional_user
from app.modules.auth.models import User
from app.modules.auth.role_deps import require_admin, require_customer, require_kol
from app.modules.auth.schemas import UserResponse
from app.modules.booking.schemas import (
    BookingActivityLogResponse,
    BookingCreateRequest,
    BookingProgressUpdateRequest,
    BookingResponse,
    BookingStatusUpdateRequest,
    DashboardStatsResponse,
    KolManualBookingCreateRequest,
    KolPublicCard,
    PaymentReviewRequest,
)
from app.modules.booking.services import (
    create_booking,
    create_manual_booking,
    get_booking_detail,
    get_dashboard_stats,
    get_kol_dashboard_stats,
    list_bookings_for_admin,
    list_bookings_for_customer,
    list_bookings_for_kol,
    list_booking_logs_for_kol,
    list_public_kols,
    review_payment_proof,
    serialize_booking_logs,
    submit_payment_proof,
    update_booking_progress,
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
def admin_dashboard(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
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


customer_router = APIRouter(prefix="/customer", tags=["customer"])


@customer_router.get("/bookings", response_model=list[BookingResponse])
def customer_list_bookings(
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
) -> list[BookingResponse]:
    return [
        BookingResponse.model_validate(item)
        for item in list_bookings_for_customer(db, current_user.id)
    ]


@customer_router.post("/bookings/{booking_id}/payment-proof", response_model=BookingResponse)
async def customer_submit_payment_proof(
    booking_id: UUID,
    file: UploadFile = File(...),
    note: str | None = Form(default=None),
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
) -> BookingResponse:
    try:
        proof_url = await save_payment_proof(file)
        submit_payment_proof(db, booking_id, current_user.id, proof_url, note)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    detail = get_booking_detail(db, booking_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")
    return BookingResponse.model_validate(detail)


kol_router = APIRouter(prefix="/kol", tags=["kol"])


@kol_router.get("/dashboard", response_model=DashboardStatsResponse)
def kol_dashboard(current_user: User = Depends(require_kol), db: Session = Depends(get_db)) -> DashboardStatsResponse:
    if current_user.role != "kol":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="KOL account required.")
    return get_kol_dashboard_stats(db, current_user.id)


@kol_router.get("/bookings", response_model=list[BookingResponse])
def kol_list_bookings(current_user: User = Depends(require_kol), db: Session = Depends(get_db)) -> list[BookingResponse]:
    if current_user.role != "kol":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="KOL account required.")
    return [BookingResponse.model_validate(item) for item in list_bookings_for_kol(db, current_user.id)]


@kol_router.get("/bookings/{booking_id}/logs", response_model=list[BookingActivityLogResponse])
def kol_list_booking_logs(
    booking_id: UUID,
    current_user: User = Depends(require_kol),
    db: Session = Depends(get_db),
) -> list[BookingActivityLogResponse]:
    try:
        logs = list_booking_logs_for_kol(db, booking_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return [BookingActivityLogResponse.model_validate(item) for item in serialize_booking_logs(logs)]


@kol_router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def kol_create_manual_booking(
    payload: KolManualBookingCreateRequest,
    current_user: User = Depends(require_kol),
    db: Session = Depends(get_db),
) -> BookingResponse:
    try:
        booking = create_manual_booking(db, current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    detail = get_booking_detail(db, booking.id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to load booking.")
    return BookingResponse.model_validate(detail)


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


@kol_router.patch("/bookings/{booking_id}/payment-review", response_model=BookingResponse)
def kol_review_payment(
    booking_id: UUID,
    payload: PaymentReviewRequest,
    current_user: User = Depends(require_kol),
    db: Session = Depends(get_db),
) -> BookingResponse:
    if current_user.role != "kol":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="KOL account required.")
    try:
        review_payment_proof(db, booking_id, current_user.id, payload.action, payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    detail = get_booking_detail(db, booking_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")
    return BookingResponse.model_validate(detail)


@kol_router.patch("/bookings/{booking_id}/progress", response_model=BookingResponse)
def kol_update_booking_progress(
    booking_id: UUID,
    payload: BookingProgressUpdateRequest,
    current_user: User = Depends(require_kol),
    db: Session = Depends(get_db),
) -> BookingResponse:
    try:
        update_booking_progress(
            db,
            booking_id,
            current_user.id,
            payload.progress_percent,
            payload.progress_note,
            payload.extended_until,
            payload.extension_note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    detail = get_booking_detail(db, booking_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")
    return BookingResponse.model_validate(detail)
