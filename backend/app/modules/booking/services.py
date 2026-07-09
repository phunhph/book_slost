import json
from datetime import UTC, datetime
from urllib.parse import quote
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.modules.auth.models import User
from app.modules.booking.models import Booking, BookingActivityLog
from app.modules.booking.schemas import BookingCreateRequest, KolManualBookingCreateRequest, KolPublicCard
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
        "payment_proof_url": booking.payment_proof_url,
        "payment_proof_note": booking.payment_proof_note,
        "payment_proof_uploaded_at": booking.payment_proof_uploaded_at,
        "payment_reviewed_at": booking.payment_reviewed_at,
        "source": booking.source,
        "progress_percent": booking.progress_percent,
        "progress_note": booking.progress_note,
        "extension_count": booking.extension_count,
        "extended_until": booking.extended_until,
        "extension_note": booking.extension_note,
        "progress_updated_at": booking.progress_updated_at,
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


def _serialize_booking_log(item: BookingActivityLog) -> dict:
    return {
        "id": item.id,
        "booking_id": item.booking_id,
        "actor_user_id": item.actor_user_id,
        "actor_role": item.actor_role,
        "action": item.action,
        "message": item.message,
        "metadata": json.loads(item.metadata_json) if item.metadata_json else None,
        "created_at": item.created_at,
    }


def _append_booking_log(
    db: Session,
    booking_id: UUID,
    action: str,
    message: str,
    actor: User | None = None,
    metadata: dict | None = None,
) -> None:
    db.add(
        BookingActivityLog(
            booking_id=booking_id,
            actor_user_id=actor.id if actor else None,
            actor_role=actor.role if actor else None,
            action=action,
            message=message,
            metadata_json=json.dumps(metadata, ensure_ascii=False) if metadata else None,
        )
    )


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
    _append_booking_log(
        db,
        booking.id,
        action="booking_created",
        message="Tạo booking mới từ luồng đặt lịch.",
        actor=current_user,
        metadata={
            "source": "public" if current_user is None else "customer",
            "scheduled_at": payload.scheduled_at.isoformat(),
            "pricing_type": pricing_type,
            "quantity": quantity,
        },
    )

    db.commit()
    db.refresh(booking)
    return booking


def create_manual_booking(
    db: Session,
    kol_user_id: UUID,
    payload: KolManualBookingCreateRequest,
) -> Booking:
    kol = db.get(User, kol_user_id)
    if not kol or kol.role != "kol" or not kol.is_active:
        raise ValueError("Không tìm thấy KOL.")

    kol_profile = db.scalar(select(UserProfile).where(UserProfile.user_id == kol.id))
    if not kol_profile:
        raise ValueError("KOL chưa có hồ sơ.")

    pricing_type = payload.pricing_type or kol_profile.pricing_type or "match"
    unit_price = kol_profile.price_per_match if pricing_type == "match" else kol_profile.price_per_hour
    if unit_price <= 0:
        raise ValueError("Bạn chưa thiết lập giá booking.")

    quantity = payload.quantity or 1
    total_amount = unit_price * quantity

    booking = Booking(
        kol_user_id=kol_user_id,
        customer_user_id=None,
        guest_name=(payload.guest_name or "").strip() or None,
        guest_phone=(payload.guest_phone or "").strip() or None,
        guest_zalo=(payload.guest_zalo or "").strip() or None,
        guest_messenger=(payload.guest_messenger or "").strip() or None,
        scheduled_at=payload.scheduled_at,
        pricing_type=pricing_type,
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        currency=kol_profile.currency or "VND",
        payment_status="unpaid",
        notes=(payload.notes or "").strip() or None,
        status="pending",
        source=payload.source,
        progress_percent=0,
    )
    db.add(booking)
    db.flush()

    short_id = str(booking.id).replace("-", "")[:8].upper()
    booking.payment_code = f"BK{short_id}"
    if _has_bank_account(kol_profile):
        booking.payment_qr_url = _build_vietqr_url(booking, kol_profile)
    _append_booking_log(
        db,
        booking.id,
        action="manual_booking_created",
        message="KOL tự tạo booking để quản lý case ngoài hệ thống.",
        actor=kol,
        metadata={
            "source": payload.source,
            "scheduled_at": payload.scheduled_at.isoformat(),
            "pricing_type": pricing_type,
            "quantity": quantity,
        },
    )

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


def list_bookings_for_customer(db: Session, customer_user_id: UUID) -> list[dict]:
    bookings = db.scalars(
        select(Booking)
        .where(Booking.customer_user_id == customer_user_id)
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

    if status == "confirmed" and booking.payment_status != "paid":
        raise ValueError(
            "Chưa thể xác nhận đặt lịch. Hãy đối chiếu bill chuyển khoản và duyệt thanh toán trước."
        )

    old_status = booking.status
    booking.status = status
    actor = db.get(User, kol_user_id) if kol_user_id else None
    _append_booking_log(
        db,
        booking.id,
        action="status_updated",
        message=f"Cập nhật trạng thái từ '{old_status}' sang '{status}'.",
        actor=actor,
        metadata={"from_status": old_status, "to_status": status},
    )
    db.commit()
    db.refresh(booking)
    return booking


def submit_payment_proof(
    db: Session,
    booking_id: UUID,
    customer_user_id: UUID,
    proof_url: str,
    note: str | None = None,
) -> Booking:
    booking = db.get(Booking, booking_id)
    if not booking:
        raise ValueError("Không tìm thấy booking.")
    if booking.customer_user_id != customer_user_id:
        raise ValueError("Bạn chỉ có thể gửi bill cho booking của mình.")
    if booking.status == "cancelled":
        raise ValueError("Booking đã hủy, không thể gửi bill.")
    if booking.payment_status == "paid":
        raise ValueError("Thanh toán đã được duyệt, không cần gửi lại bill.")

    booking.payment_proof_url = proof_url
    booking.payment_proof_note = (note or "").strip() or None
    booking.payment_proof_uploaded_at = datetime.now(UTC)
    booking.payment_reviewed_at = None
    booking.payment_status = "proof_submitted"
    actor = db.get(User, customer_user_id)
    _append_booking_log(
        db,
        booking.id,
        action="payment_proof_submitted",
        message="Khách đã gửi bill chuyển khoản để đối soát.",
        actor=actor,
        metadata={"note": booking.payment_proof_note, "proof_url": proof_url},
    )
    db.commit()
    db.refresh(booking)
    return booking


def review_payment_proof(
    db: Session,
    booking_id: UUID,
    kol_user_id: UUID,
    action: str,
    note: str | None = None,
) -> Booking:
    booking = db.get(Booking, booking_id)
    if not booking:
        raise ValueError("Không tìm thấy booking.")
    if booking.kol_user_id != kol_user_id:
        raise ValueError("Bạn chỉ có thể duyệt thanh toán booking của mình.")
    if not booking.payment_proof_url:
        raise ValueError("Khách chưa gửi bill chuyển khoản.")
    if booking.payment_status not in {"proof_submitted", "paid", "unpaid"}:
        raise ValueError("Trạng thái thanh toán không hợp lệ để duyệt.")

    normalized = action.strip().lower()
    review_note = (note or "").strip() or None

    if normalized == "approve":
        booking.payment_status = "paid"
        booking.payment_reviewed_at = datetime.now(UTC)
        if review_note:
            booking.payment_proof_note = review_note
        # Auto-confirm schedule after matching payment proof
        if booking.status == "pending":
            booking.status = "confirmed"
    elif normalized == "reject":
        booking.payment_status = "unpaid"
        booking.payment_reviewed_at = datetime.now(UTC)
        booking.payment_proof_note = review_note or "Bill không khớp. Vui lòng gửi lại biên lai đúng."
        if booking.status == "confirmed":
            booking.status = "pending"
    else:
        raise ValueError("Hành động duyệt không hợp lệ.")

    actor = db.get(User, kol_user_id)
    _append_booking_log(
        db,
        booking.id,
        action="payment_reviewed",
        message="KOL đã duyệt trạng thái thanh toán." if normalized == "approve" else "KOL đã từ chối bill thanh toán.",
        actor=actor,
        metadata={"action": normalized, "note": booking.payment_proof_note, "payment_status": booking.payment_status},
    )
    db.commit()
    db.refresh(booking)
    return booking


def update_booking_progress(
    db: Session,
    booking_id: UUID,
    kol_user_id: UUID,
    progress_percent: int,
    progress_note: str | None = None,
    extended_until: datetime | None = None,
    extension_note: str | None = None,
) -> Booking:
    booking = db.get(Booking, booking_id)
    if not booking:
        raise ValueError("Không tìm thấy booking.")
    if booking.kol_user_id != kol_user_id:
        raise ValueError("Bạn chỉ có thể cập nhật booking của mình.")
    if booking.status == "cancelled":
        raise ValueError("Booking đã hủy, không thể cập nhật tiến độ.")

    scheduled_at = booking.scheduled_at
    if scheduled_at.tzinfo is None:
        scheduled_at = scheduled_at.replace(tzinfo=UTC)
    if extended_until and extended_until < scheduled_at:
        raise ValueError("Ngày gia hạn phải sau lịch hiện tại.")

    booking.progress_percent = progress_percent
    booking.progress_note = (progress_note or "").strip() or None
    booking.progress_updated_at = datetime.now(UTC)
    if extended_until:
        booking.extension_count = (booking.extension_count or 0) + 1
        booking.extended_until = extended_until
        booking.extension_note = (extension_note or "").strip() or None
    actor = db.get(User, kol_user_id)
    _append_booking_log(
        db,
        booking.id,
        action="progress_updated",
        message="KOL đã cập nhật tiến độ booking.",
        actor=actor,
        metadata={
            "progress_percent": booking.progress_percent,
            "progress_note": booking.progress_note,
            "extended_until": booking.extended_until.isoformat() if booking.extended_until else None,
            "extension_count": booking.extension_count,
            "extension_note": booking.extension_note,
        },
    )

    db.commit()
    db.refresh(booking)
    return booking


def list_booking_logs_for_kol(db: Session, booking_id: UUID, kol_user_id: UUID) -> list[BookingActivityLog]:
    booking = db.get(Booking, booking_id)
    if not booking:
        raise ValueError("Không tìm thấy booking.")
    if booking.kol_user_id != kol_user_id:
        raise ValueError("Bạn chỉ có thể xem log booking của mình.")
    return db.scalars(
        select(BookingActivityLog).where(BookingActivityLog.booking_id == booking_id).order_by(BookingActivityLog.created_at.desc())
    ).all()


def serialize_booking_logs(items: list[BookingActivityLog]) -> list[dict]:
    return [_serialize_booking_log(item) for item in items]


def get_dashboard_stats(db: Session) -> dict:
    total_kols = db.scalar(select(func.count()).select_from(User).where(User.role == "kol")) or 0
    total_customers = db.scalar(select(func.count()).select_from(User).where(User.role == "customer")) or 0
    total_bookings = db.scalar(select(func.count()).select_from(Booking)) or 0
    pending_bookings = (
        db.scalar(select(func.count()).select_from(Booking).where(Booking.status == "pending")) or 0
    )
    confirmed_bookings = (
        db.scalar(select(func.count()).select_from(Booking).where(Booking.status == "confirmed")) or 0
    )
    completed_bookings = (
        db.scalar(select(func.count()).select_from(Booking).where(Booking.status == "completed")) or 0
    )
    cancelled_bookings = (
        db.scalar(select(func.count()).select_from(Booking).where(Booking.status == "cancelled")) or 0
    )

    bookings = db.scalars(
        select(Booking)
        .options(joinedload(Booking.kol).joinedload(User.profile))
        .order_by(Booking.scheduled_at.asc())
    ).all()

    now = datetime.now(UTC)
    current_year = now.year
    current_month = now.month

    def _is_revenue_booking(booking: Booking) -> bool:
        return booking.status != "cancelled"

    def _is_collected(booking: Booking) -> bool:
        return _is_revenue_booking(booking) and (
            booking.payment_status == "paid" or booking.status == "completed"
        )

    gross_revenue = sum(b.total_amount or 0 for b in bookings if _is_revenue_booking(b))
    collected_revenue = sum(b.total_amount or 0 for b in bookings if _is_collected(b))
    unpaid_revenue = sum(
        b.total_amount or 0
        for b in bookings
        if _is_revenue_booking(b) and not _is_collected(b)
    )

    month_gross = 0
    month_collected = 0
    year_gross = 0
    year_collected = 0
    for booking in bookings:
        if not _is_revenue_booking(booking):
            continue
        scheduled = booking.scheduled_at
        if scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=UTC)
        amount = booking.total_amount or 0
        if scheduled.year == current_year:
            year_gross += amount
            if _is_collected(booking):
                year_collected += amount
            if scheduled.month == current_month:
                month_gross += amount
                if _is_collected(booking):
                    month_collected += amount

    # Last 12 months revenue series
    monthly_labels: list[str] = []
    monthly_gross: list[int] = []
    monthly_collected: list[int] = []
    monthly_booking_counts: list[int] = []
    for offset in range(11, -1, -1):
        year = current_year
        month = current_month - offset
        while month <= 0:
            month += 12
            year -= 1
        label = f"{month:02d}/{year}"
        monthly_labels.append(label)
        g = 0
        c = 0
        count = 0
        for booking in bookings:
            if not _is_revenue_booking(booking):
                continue
            scheduled = booking.scheduled_at
            if scheduled.tzinfo is None:
                scheduled = scheduled.replace(tzinfo=UTC)
            if scheduled.year == year and scheduled.month == month:
                amount = booking.total_amount or 0
                g += amount
                count += 1
                if _is_collected(booking):
                    c += amount
        monthly_gross.append(g)
        monthly_collected.append(c)
        monthly_booking_counts.append(count)

    # Last 5 years revenue series
    yearly_labels: list[str] = []
    yearly_gross: list[int] = []
    yearly_collected: list[int] = []
    yearly_booking_counts: list[int] = []
    for year in range(current_year - 4, current_year + 1):
        yearly_labels.append(str(year))
        g = 0
        c = 0
        count = 0
        for booking in bookings:
            if not _is_revenue_booking(booking):
                continue
            scheduled = booking.scheduled_at
            if scheduled.tzinfo is None:
                scheduled = scheduled.replace(tzinfo=UTC)
            if scheduled.year == year:
                amount = booking.total_amount or 0
                g += amount
                count += 1
                if _is_collected(booking):
                    c += amount
        yearly_gross.append(g)
        yearly_collected.append(c)
        yearly_booking_counts.append(count)

    # Top KOLs by collected revenue
    kol_revenue: dict[str, dict] = {}
    for booking in bookings:
        if not _is_collected(booking):
            continue
        kol_profile = booking.kol.profile if booking.kol else None
        key = str(booking.kol_user_id)
        if key not in kol_revenue:
            kol_revenue[key] = {
                "kol_user_id": key,
                "display_name": (kol_profile.display_name if kol_profile else None)
                or (kol_profile.username if kol_profile else None)
                or "KOL",
                "username": kol_profile.username if kol_profile else None,
                "revenue": 0,
                "bookings": 0,
            }
        kol_revenue[key]["revenue"] += booking.total_amount or 0
        kol_revenue[key]["bookings"] += 1

    top_kols = sorted(kol_revenue.values(), key=lambda item: item["revenue"], reverse=True)[:8]

    return {
        "total_kols": total_kols,
        "total_customers": total_customers,
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "confirmed_bookings": confirmed_bookings,
        "completed_bookings": completed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "currency": "VND",
        "gross_revenue": gross_revenue,
        "collected_revenue": collected_revenue,
        "unpaid_revenue": unpaid_revenue,
        "month_gross_revenue": month_gross,
        "month_collected_revenue": month_collected,
        "year_gross_revenue": year_gross,
        "year_collected_revenue": year_collected,
        "revenue_by_month": {
            "labels": monthly_labels,
            "gross": monthly_gross,
            "collected": monthly_collected,
            "booking_counts": monthly_booking_counts,
        },
        "revenue_by_year": {
            "labels": yearly_labels,
            "gross": yearly_gross,
            "collected": yearly_collected,
            "booking_counts": yearly_booking_counts,
        },
        "top_kols_by_revenue": top_kols,
    }


def get_kol_dashboard_stats(db: Session, kol_user_id: UUID) -> dict:
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

    bookings = db.scalars(select(Booking).where(Booking.kol_user_id == kol_user_id)).all()
    completed_bookings = sum(1 for b in bookings if b.status == "completed")
    confirmed_bookings = sum(1 for b in bookings if b.status == "confirmed")
    cancelled_bookings = sum(1 for b in bookings if b.status == "cancelled")
    proof_submitted_bookings = sum(1 for b in bookings if b.payment_status == "proof_submitted")
    collected_revenue = sum(
        b.total_amount or 0
        for b in bookings
        if b.status != "cancelled" and (b.payment_status == "paid" or b.status == "completed")
    )
    unpaid_revenue = sum(
        b.total_amount or 0
        for b in bookings
        if b.status != "cancelled" and not (b.payment_status == "paid" or b.status == "completed")
    )

    now = datetime.now(UTC)
    current_year = now.year
    current_month = now.month
    monthly_labels: list[str] = []
    monthly_gross: list[int] = []
    monthly_collected: list[int] = []
    monthly_booking_counts: list[int] = []
    for offset in range(11, -1, -1):
        year = current_year
        month = current_month - offset
        while month <= 0:
            month += 12
            year -= 1
        monthly_labels.append(f"{month:02d}/{year}")
        gross = 0
        collected = 0
        count = 0
        for booking in bookings:
            scheduled = booking.scheduled_at
            if scheduled.tzinfo is None:
                scheduled = scheduled.replace(tzinfo=UTC)
            if scheduled.year == year and scheduled.month == month and booking.status != "cancelled":
                gross += booking.total_amount or 0
                count += 1
                if booking.payment_status == "paid" or booking.status == "completed":
                    collected += booking.total_amount or 0
        monthly_gross.append(gross)
        monthly_collected.append(collected)
        monthly_booking_counts.append(count)

    return {
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "upcoming_bookings": upcoming_bookings,
        "collected_revenue": collected_revenue,
        "unpaid_revenue": unpaid_revenue,
        "completed_bookings": completed_bookings,
        "confirmed_bookings": confirmed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "proof_submitted_bookings": proof_submitted_bookings,
        "revenue_by_month": {
            "labels": monthly_labels,
            "gross": monthly_gross,
            "collected": monthly_collected,
            "booking_counts": monthly_booking_counts,
        },
    }
