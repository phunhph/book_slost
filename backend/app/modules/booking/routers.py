from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.uploads import save_payment_proof
from app.modules.auth.deps import get_optional_user
from app.modules.auth.models import User
from app.modules.auth.role_deps import require_admin, require_customer, require_kol
from app.modules.auth.schemas import (
    UserResponse,
    AdminUserResponse,
    AdminUserCreateRequest,
    AdminUserUpdateRequest,
)
from app.modules.auth.services import hash_password
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
from app.modules.profile.services import ensure_profile_layout_v2
from app.modules.profile.schemas import (
    SocialPlatformResponse,
    SocialPlatformCreateRequest,
    SocialPlatformUpdateRequest,
)


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


def sync_profile_contacts(profile: UserProfile, contact_links: list[dict], phone: str | None = None):
    profile.contact_links = contact_links
    phone_val = phone
    zalo_val = None
    messenger_val = None
    for link in contact_links:
        plat = link.get("platform")
        val = link.get("value")
        if plat == "phone" and not phone_val:
            phone_val = val
        elif plat == "zalo":
            zalo_val = val
        elif plat == "messenger":
            messenger_val = val
    profile.phone = phone_val
    profile.zalo = zalo_val
    profile.messenger = messenger_val


def get_profile_social_links(profile: UserProfile | None) -> list[dict]:
    if not profile or not profile.layout_structure:
        return []
    layout = profile.layout_structure
    if not isinstance(layout, dict) or "blocks" not in layout:
        return []
    for block in layout["blocks"]:
        if block.get("type") == "social_links":
            return block.get("data", {}).get("items", [])
    return []


def sync_profile_social_links(profile: UserProfile, social_links: list[dict]):
    ensure_profile_layout_v2(profile)
    layout = profile.layout_structure
    if not isinstance(layout, dict) or "blocks" not in layout:
        return
    for block in layout["blocks"]:
        if block.get("type") == "social_links":
            if "data" not in block or not isinstance(block["data"], dict):
                block["data"] = {}
            block["data"]["items"] = social_links
            break
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(profile, "layout_structure")


@admin_router.get("/users", response_model=list[AdminUserResponse])
def admin_list_users(
    role: str | None = None,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminUserResponse]:
    stmt = (
        select(User)
        .options(joinedload(User.profile))
        .order_by(User.created_at.desc())
    )
    if role:
        stmt = stmt.where(User.role == role)
    users = db.scalars(stmt).all()
    
    result = []
    for u in users:
        result.append(
            AdminUserResponse(
                id=u.id,
                email=u.email,
                role=u.role,
                is_active=u.is_active,
                created_at=u.created_at,
                updated_at=u.updated_at,
                display_name=u.profile.display_name if u.profile else None,
                username=u.profile.username if u.profile else None,
                phone=u.profile.phone if u.profile else None,
                contact_links=u.profile.contact_links if u.profile else [],
                social_links=get_profile_social_links(u.profile),
            )
        )
    return result


@admin_router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
def admin_create_user(
    payload: AdminUserCreateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    existing_user = db.scalar(select(User).where(User.email == payload.email))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists.")

    if payload.username:
        existing_profile = db.scalar(select(UserProfile).where(UserProfile.username == payload.username))
        if existing_profile:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists.")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        auth_provider="local",
        role=payload.role,
        is_active=payload.is_active,
    )
    profile = UserProfile(
        user=user,
        username=payload.username,
        display_name=payload.display_name,
    )
    sync_profile_contacts(profile, payload.contact_links, payload.phone)
    sync_profile_social_links(profile, payload.social_links)

    try:
        db.add(user)
        db.add(profile)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    db.refresh(user)
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        display_name=profile.display_name,
        username=profile.username,
        phone=profile.phone,
        contact_links=profile.contact_links,
        social_links=get_profile_social_links(profile),
    )


@admin_router.put("/users/{user_id}", response_model=AdminUserResponse)
def admin_update_user(
    user_id: UUID,
    payload: AdminUserUpdateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    user = db.scalar(select(User).options(joinedload(User.profile)).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if payload.email and payload.email != user.email:
        existing_user = db.scalar(select(User).where(User.email == payload.email))
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists.")

    if payload.username and user.profile and payload.username != user.profile.username:
        existing_profile = db.scalar(select(UserProfile).where(UserProfile.username == payload.username))
        if existing_profile:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists.")

    if payload.email is not None:
        user.email = payload.email
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.role is not None:
        user.role = payload.role
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)

    if not user.profile:
        user.profile = UserProfile(user_id=user.id)

    if payload.display_name is not None:
        user.profile.display_name = payload.display_name
    if payload.username is not None:
        user.profile.username = payload.username

    if payload.contact_links is not None:
        sync_profile_contacts(user.profile, payload.contact_links, payload.phone)
    elif payload.phone is not None:
        user.profile.phone = payload.phone

    if payload.social_links is not None:
        sync_profile_social_links(user.profile, payload.social_links)

    try:
        db.add(user)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    db.refresh(user)
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        display_name=user.profile.display_name,
        username=user.profile.username,
        phone=user.profile.phone,
        contact_links=user.profile.contact_links,
        social_links=get_profile_social_links(user.profile),
    )


@admin_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(
    user_id: UUID,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    try:
        db.delete(user)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@admin_router.get("/platforms", response_model=list[SocialPlatformResponse])
def admin_list_platforms(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[SocialPlatformResponse]:
    from app.modules.profile.models import SocialPlatform
    stmt = select(SocialPlatform).order_by(SocialPlatform.category.desc(), SocialPlatform.label.asc())
    return db.scalars(stmt).all()


@admin_router.post("/platforms", response_model=SocialPlatformResponse, status_code=status.HTTP_201_CREATED)
def admin_create_platform(
    payload: SocialPlatformCreateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SocialPlatformResponse:
    from app.modules.profile.models import SocialPlatform
    existing = db.scalar(select(SocialPlatform).where(SocialPlatform.key == payload.key))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Platform key already exists.")

    platform = SocialPlatform(**payload.model_dump())
    try:
        db.add(platform)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    db.refresh(platform)
    return platform


@admin_router.put("/platforms/{platform_id}", response_model=SocialPlatformResponse)
def admin_update_platform(
    platform_id: UUID,
    payload: SocialPlatformUpdateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SocialPlatformResponse:
    from app.modules.profile.models import SocialPlatform
    platform = db.scalar(select(SocialPlatform).where(SocialPlatform.id == platform_id))
    if not platform:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Platform not found.")

    updates = payload.model_dump(exclude_unset=True)
    if "key" in updates and updates["key"] != platform.key:
        existing = db.scalar(select(SocialPlatform).where(SocialPlatform.key == updates["key"]))
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Platform key already exists.")

    for k, v in updates.items():
        setattr(platform, k, v)

    try:
        db.add(platform)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    db.refresh(platform)
    return platform


@admin_router.delete("/platforms/{platform_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_platform(
    platform_id: UUID,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from app.modules.profile.models import SocialPlatform
    platform = db.scalar(select(SocialPlatform).where(SocialPlatform.id == platform_id))
    if not platform:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Platform not found.")

    try:
        db.delete(platform)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


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
