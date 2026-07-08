from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.auth.schemas import RegisterLocalRequest
from app.modules.auth.services import login_local_user, register_local_user
from app.modules.booking.schemas import BookingCreateRequest
from app.modules.booking.services import (
    _has_bank_account,
    create_booking,
    get_dashboard_stats,
    update_booking_status,
)
from app.modules.profile.models import UserProfile


def test_register_and_login_local_user(db_session: Session) -> None:
    user = register_local_user(
        db_session,
        RegisterLocalRequest(
            email="new.customer@example.com",
            password="Customer@123",
            display_name="New Customer",
            username="new-customer",
        ),
    )
    assert user.role == "customer"
    assert user.email == "new.customer@example.com"

    logged_in = login_local_user(db_session, "new.customer@example.com", "Customer@123")
    assert logged_in.id == user.id


def test_register_duplicate_email_raises(db_session: Session, seed_users: dict[str, User]) -> None:
    with pytest.raises(ValueError, match="Email already exists"):
        register_local_user(
            db_session,
            RegisterLocalRequest(
                email=seed_users["customer"].email,
                password="Customer@123",
                display_name="Dup",
            ),
        )


def test_login_wrong_password_raises(db_session: Session, seed_users: dict[str, User]) -> None:
    with pytest.raises(ValueError, match="Invalid email or password"):
        login_local_user(db_session, seed_users["customer"].email, "WrongPass999")


def test_has_bank_account_requires_all_fields(db_session: Session, seed_users: dict[str, User]) -> None:
    kol_profile = db_session.get(UserProfile, seed_users["kol"].id)
    nobank_profile = db_session.get(UserProfile, seed_users["kol_no_bank"].id)
    assert kol_profile is not None
    assert nobank_profile is not None
    assert _has_bank_account(kol_profile) is True
    assert _has_bank_account(nobank_profile) is False


def test_create_booking_generates_vietqr_and_total(
    db_session: Session,
    seed_users: dict[str, User],
    future_schedule: datetime,
) -> None:
    booking = create_booking(
        db_session,
        BookingCreateRequest(
            kol_user_id=seed_users["kol"].id,
            scheduled_at=future_schedule,
            pricing_type="match",
            quantity=3,
            guest_name="Khach Test",
            guest_phone="0909111222",
            notes="3 tran Duo",
        ),
        current_user=None,
    )

    assert booking.status == "pending"
    assert booking.unit_price == 150000
    assert booking.total_amount == 450000
    assert booking.payment_code is not None
    assert booking.payment_code.startswith("BK")
    assert booking.payment_qr_url is not None
    assert "img.vietqr.io/image/970436-0123456789" in booking.payment_qr_url
    assert "amount=450000" in booking.payment_qr_url
    assert booking.payment_status == "unpaid"


def test_create_booking_rejects_kol_without_bank(
    db_session: Session,
    seed_users: dict[str, User],
    future_schedule: datetime,
) -> None:
    with pytest.raises(ValueError, match="ngân hàng"):
        create_booking(
            db_session,
            BookingCreateRequest(
                kol_user_id=seed_users["kol_no_bank"].id,
                scheduled_at=future_schedule,
                pricing_type="match",
                quantity=1,
                guest_name="Khach",
                guest_phone="0909111222",
            ),
            current_user=None,
        )


def test_create_booking_hourly_pricing_and_customer_autofill(
    db_session: Session,
    seed_users: dict[str, User],
    future_schedule: datetime,
) -> None:
    booking = create_booking(
        db_session,
        BookingCreateRequest(
            kol_user_id=seed_users["kol"].id,
            scheduled_at=future_schedule,
            pricing_type="hourly",
            quantity=2,
        ),
        current_user=seed_users["customer"],
    )

    assert booking.customer_user_id == seed_users["customer"].id
    assert booking.guest_name == "Customer Test"
    assert booking.guest_phone == "0901000002"
    assert booking.unit_price == 100000
    assert booking.total_amount == 200000


def test_update_booking_status_ownership(
    db_session: Session,
    seed_users: dict[str, User],
    future_schedule: datetime,
) -> None:
    booking = create_booking(
        db_session,
        BookingCreateRequest(
            kol_user_id=seed_users["kol"].id,
            scheduled_at=future_schedule,
            pricing_type="match",
            quantity=1,
            guest_name="Guest",
            guest_phone="0909555666",
        ),
        current_user=None,
    )

    updated = update_booking_status(db_session, booking.id, "confirmed", kol_user_id=seed_users["kol"].id)
    assert updated.status == "confirmed"

    with pytest.raises(ValueError, match="của mình"):
        update_booking_status(
            db_session,
            booking.id,
            "completed",
            kol_user_id=UUID("99999999-9999-9999-9999-999999999999"),
        )


def test_dashboard_stats_counts(db_session: Session, seed_users: dict[str, User], future_schedule: datetime) -> None:
    create_booking(
        db_session,
        BookingCreateRequest(
            kol_user_id=seed_users["kol"].id,
            scheduled_at=future_schedule,
            pricing_type="match",
            quantity=1,
            guest_name="Guest A",
            guest_phone="0909000001",
        ),
        current_user=None,
    )
    stats = get_dashboard_stats(db_session)
    assert stats["total_kols"] == 2
    assert stats["total_customers"] == 1
    assert stats["total_bookings"] == 1
    assert stats["pending_bookings"] == 1
