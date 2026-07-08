from datetime import UTC, datetime
from urllib.parse import quote
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.modules.auth.models import User
from app.modules.booking.models import Booking
from app.modules.booking.schemas import BookingCreateRequest, KolPublicCard
from app.modules.profile.models import UserProfile


def _has_bank_account(profile: UserProfile) -> bool:
    return bool(
        (profile.bank_code or "").strip()
        and (profile.bank_account_number or "").strip()
        and (profile.bank_account_name or "").strip()
    )


def _build_vietqr_url(booking: Booking, profile: UserProfile) -> str:
    bank_code = (profile.bank_code or "").strip()
    account_number = (profile.bank_account_number or "").strip()
    account_name = (profile.bank_account_name or "").strip()
    add_info = quote(f"{booking.payment_code} {booking.guest_name or ''}".strip(), safe="")
    account_name_q = quote(account_name, safe="")
    return (
        f"https://img.vietqr.io/image/{bank_code}-{account_number}-compact2.png"
        f"?amount={booking.total_amount}&addInfo={add_info}&accountName={account_name_q}"
    )


def _serialize_booking(booking: Booking) -> dict:
    kol_profile = booking.kol.profile if booking.kol else None
    customer = booking.customer
    return {
        "id": booking.id,
        "kol_user_id": booking.kol_user_id,
        "customer_user_id": booking.customer_user_id,
        "guest_name": booking.guest_name,
        "guest_phone": booking.guest_phone,
        "guest_zalo": booking.guest_zalo,
        "guest_messenger": booking.guest_messenger,
        "scheduled_at": booking.scheduled_at,
        "pricing_type": booking.pricing_type,
        "quantity": booking.quantity,
        "unit_price": booking.unit_price,
        "total_amount": booking.total_amount,
        "currency": booking.currency,
        "payment_qr_url": booking.payment_qr_url,
        "payment_code": booking.payment_code,
        "payment_status": booking.payment_status,
        "status": booking.status,
        "notes": booking.notes,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at,
        "kol_display_name": kol_profile.display_name if kol_profile else None,
        "kol_username": kol_profile.username if kol_profile else None,
        "customer_email": customer.email if customer else None,
        "bank_name": kol_profile.bank_name if kol_profile else None,
        "bank_account_number": kol_profile.bank_account_number if kol_profile else None,
        "bank_account_name": kol_profile.bank_account_name if kol_profile else None,
    }


def list_public_kols(db: Session) -> list[KolPublicCard]:
    stmt = (
        select(User, UserProfile)
        .join(UserProfile, UserProfile.user_id == User.id)
        .where(User.role == "kol", User.is_active.is_(True), UserProfile.username.is_not(None))
        .order_by(UserProfile.display_name.asc())
    )
    rows = db.execute(stmt).all()
    return [
        KolPublicCard(
            user_id=user.id,
            username=profile.username,
            display_name=profile.display_name,
            bio=profile.bio,
            avatar_url=profile.avatar_url,
            primary_color=profile.primary_color,
            pricing_type=profile.pricing_type,
            price_per_match=profile.price_per_match,
            price_per_hour=profile.price_per_hour,
            currency=profile.currency,
            has_bank_account=_has_bank_account(profile),
        )
        for user, profile in rows
    ]


def get_booking_detail(db: Session, booking_id: UUID) -> dict | None:
    booking = db.scalar(
        select(Booking)
        .options(joinedload(Booking.kol).joinedload(User.profile), joinedload(Booking.customer))
        .where(Booking.id == booking_id)
    )
    if not booking:
        return None
    return _serialize_booking(booking)


def create_booking(
    db: Session,
    payload: BookingCreateRequest,
    current_user: User | None,
) -> Booking:
    kol = db.get(User, payload.kol_user_id)
    if not kol or kol.role != "kol" or not kol.is_active:
        raise ValueError("Không tìm thấy KOL.")

    kol_profile = db.scalar(select(UserProfile).where(UserProfile.user_id == kol.id))
    if not kol_profile:
        raise ValueError("KOL chưa có hồ sơ.")

    if not _has_bank_account(kol_profile):
        raise ValueError(
            "KOL chưa cấu hình tài khoản ngân hàng nên chưa tạo được mã QR thanh toán. "
            "Vui lòng liên hệ KOL."
        )

    pricing_type = payload.pricing_type or kol_profile.pricing_type or "match"
    unit_price = (
        kol_profile.price_per_match if pricing_type == "match" else kol_profile.price_per_hour
    )
    if unit_price <= 0:
        raise ValueError("KOL chưa thiết lập giá. Vui lòng liên hệ KOL.")

    quantity = payload.quantity or 1
    if quantity < 1:
        raise ValueError("Số lượng phải từ 1 trở lên.")

    total_amount = unit_price * quantity
    currency = kol_profile.currency or "VND"

    guest_name = (payload.guest_name or "").strip() or None
    guest_phone = (payload.guest_phone or "").strip() or None
    guest_zalo = (payload.guest_zalo or "").strip() or None
    guest_messenger = (payload.guest_messenger or "").strip() or None
    customer_user_id = None

    if current_user:
        customer_user_id = current_user.id
        profile = db.scalar(select(UserProfile).where(UserProfile.user_id == current_user.id))
        guest_name = guest_name or (profile.display_name if profile else None) or current_user.email
        guest_phone = guest_phone or (profile.phone if profile else None)
        guest_zalo = guest_zalo or (profile.zalo if profile else None)
        guest_messenger = guest_messenger or (profile.messenger if profile else None)
    else:
        if not guest_name:
            raise ValueError("Vui lòng nhập họ tên.")
        if not guest_phone:
            raise ValueError("Số điện thoại là bắt buộc khi đặt lịch khách.")

    if not guest_phone:
        raise ValueError("Vui lòng nhập số điện thoại.")

    booking = Booking(
        kol_user_id=payload.kol_user_id,
        customer_user_id=customer_user_id,
        guest_name=guest_name,
        guest_phone=guest_phone,
        guest_zalo=guest_zalo,
        guest_messenger=guest_messenger,
        scheduled_at=payload.scheduled_at,
        pricing_type=pricing_type,
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        currency=currency,
        payment_status="unpaid",
        notes=payload.notes,
        status="pending",
    )
    db.add(booking)
    db.flush()

    short_id = str(booking.id).replace("-", "")[:8].upper()
    booking.payment_code = f"BK{short_id}"
    booking.payment_qr_url = _build_vietqr_url(booking, kol_profile)

    db.commit()
    db.refresh(booking)
    return booking


def list_bookings_for_admin(db: Session) -> list[dict]:
    bookings = db.scalars(
        select(Booking)
        .options(joinedload(Booking.kol).joinedload(User.profile), joinedload(Booking.customer))
        .order_by(Booking.scheduled_at.desc())
    ).all()
    return [_serialize_booking(booking) for booking in bookings]


def list_bookings_for_kol(db: Session, kol_user_id: UUID) -> list[dict]:
    bookings = db.scalars(
        select(Booking)
        .where(Booking.kol_user_id == kol_user_id)
        .options(joinedload(Booking.kol).joinedload(User.profile), joinedload(Booking.customer))
        .order_by(Booking.scheduled_at.desc())
    ).all()
    return [_serialize_booking(booking) for booking in bookings]


def update_booking_status(db: Session, booking_id: UUID, status: str, kol_user_id: UUID | None = None) -> Booking:
    booking = db.get(Booking, booking_id)
    if not booking:
        raise ValueError("Không tìm thấy booking.")
    if kol_user_id and booking.kol_user_id != kol_user_id:
        raise ValueError("Bạn chỉ có thể cập nhật booking của mình.")

    booking.status = status
    db.commit()
    db.refresh(booking)
    return booking


def get_dashboard_stats(db: Session) -> dict[str, int]:
    total_kols = db.scalar(select(func.count()).select_from(User).where(User.role == "kol")) or 0
    total_customers = db.scalar(select(func.count()).select_from(User).where(User.role == "customer")) or 0
    total_bookings = db.scalar(select(func.count()).select_from(Booking)) or 0
    pending_bookings = (
        db.scalar(select(func.count()).select_from(Booking).where(Booking.status == "pending")) or 0
    )
    return {
        "total_kols": total_kols,
        "total_customers": total_customers,
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
    }


def get_kol_dashboard_stats(db: Session, kol_user_id: UUID) -> dict[str, int]:
    total_bookings = (
        db.scalar(select(func.count()).select_from(Booking).where(Booking.kol_user_id == kol_user_id)) or 0
    )
    pending_bookings = (
        db.scalar(
            select(func.count())
            .select_from(Booking)
            .where(Booking.kol_user_id == kol_user_id, Booking.status == "pending")
        )
        or 0
    )
    upcoming_bookings = (
        db.scalar(
            select(func.count())
            .select_from(Booking)
            .where(
                Booking.kol_user_id == kol_user_id,
                Booking.scheduled_at >= datetime.now(UTC),
                Booking.status.in_(["pending", "confirmed"]),
            )
        )
        or 0
    )
    return {
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "upcoming_bookings": upcoming_bookings,
    }
