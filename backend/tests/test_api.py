from datetime import datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.booking.models import Booking


def _auth_header(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post(
        "/api/auth/login-local",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_login_and_me_flow(client: TestClient) -> None:
    register = client.post(
        "/api/auth/register-local",
        json={
            "email": "api.customer@example.com",
            "password": "Customer@123",
            "display_name": "API Customer",
            "username": "api-customer",
        },
    )
    assert register.status_code == 201
    body = register.json()
    assert body["user"]["role"] == "customer"
    assert body["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "api.customer@example.com"


def test_login_invalid_credentials(client: TestClient, seed_users: dict[str, User]) -> None:
    response = client.post(
        "/api/auth/login-local",
        json={"email": seed_users["customer"].email, "password": "bad-password"},
    )
    assert response.status_code == 401


def test_public_kols_lists_only_active_kol_profiles(client: TestClient, seed_users: dict[str, User]) -> None:
    response = client.get("/api/public/kols")
    assert response.status_code == 200
    rows = response.json()
    usernames = {item["username"] for item in rows}
    assert "kol-test" in usernames
    assert "kol-nobank" in usernames
    with_bank = next(item for item in rows if item["username"] == "kol-test")
    without_bank = next(item for item in rows if item["username"] == "kol-nobank")
    assert with_bank["has_bank_account"] is True
    assert without_bank["has_bank_account"] is False


def test_create_booking_api_success(
    client: TestClient,
    seed_users: dict[str, User],
    future_schedule: datetime,
) -> None:
    response = client.post(
        "/api/bookings",
        json={
            "kol_user_id": str(seed_users["kol"].id),
            "scheduled_at": future_schedule.isoformat(),
            "pricing_type": "match",
            "quantity": 2,
            "guest_name": "API Guest",
            "guest_phone": "0912345678",
            "notes": "Test booking api",
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["total_amount"] == 300000
    assert data["payment_code"].startswith("BK")
    assert data["payment_qr_url"]
    assert data["bank_account_number"] == "0123456789"
    assert data["status"] == "pending"


def test_create_booking_api_requires_bank(
    client: TestClient,
    seed_users: dict[str, User],
    future_schedule: datetime,
) -> None:
    response = client.post(
        "/api/bookings",
        json={
            "kol_user_id": str(seed_users["kol_no_bank"].id),
            "scheduled_at": future_schedule.isoformat(),
            "pricing_type": "match",
            "quantity": 1,
            "guest_name": "API Guest",
            "guest_phone": "0912345678",
        },
    )
    assert response.status_code == 400
    assert "ngan hang" in response.json()["detail"].lower() or "ngân hàng" in response.json()["detail"].lower()


def test_admin_dashboard_requires_admin_role(client: TestClient, seed_users: dict[str, User]) -> None:
    customer_headers = _auth_header(client, seed_users["customer"].email, "Customer@123")
    forbidden = client.get("/api/admin/dashboard", headers=customer_headers)
    assert forbidden.status_code == 403

    admin_headers = _auth_header(client, seed_users["admin"].email, "Admin@123")
    ok = client.get("/api/admin/dashboard", headers=admin_headers)
    assert ok.status_code == 200
    payload = ok.json()
    assert payload["total_kols"] >= 2
    assert "pending_bookings" in payload
    assert "collected_revenue" in payload
    assert "revenue_by_month" in payload
    assert "revenue_by_year" in payload
    assert len(payload["revenue_by_month"]["labels"]) == 12
    assert len(payload["revenue_by_year"]["labels"]) == 5


def test_kol_can_update_own_booking_status(
    client: TestClient,
    db_session: Session,
    seed_users: dict[str, User],
    future_schedule: datetime,
) -> None:
    created = client.post(
        "/api/bookings",
        json={
            "kol_user_id": str(seed_users["kol"].id),
            "scheduled_at": future_schedule.isoformat(),
            "pricing_type": "hourly",
            "quantity": 1,
            "guest_name": "Status Guest",
            "guest_phone": "0909123456",
        },
    )
    assert created.status_code == 201
    booking_id = created.json()["id"]

    blocked = client.patch(
        f"/api/kol/bookings/{booking_id}",
        headers=_auth_header(client, seed_users["kol"].email, "Creator@123"),
        json={"status": "confirmed"},
    )
    assert blocked.status_code == 400

    booking = db_session.get(Booking, UUID(booking_id))
    assert booking is not None
    booking.payment_status = "paid"
    db_session.commit()

    kol_headers = _auth_header(client, seed_users["kol"].email, "Creator@123")
    updated = client.patch(
        f"/api/kol/bookings/{booking_id}",
        headers=kol_headers,
        json={"status": "confirmed"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "confirmed"


def test_kol_can_create_manual_booking_and_update_progress(
    client: TestClient,
    seed_users: dict[str, User],
    future_schedule: datetime,
) -> None:
    kol_headers = _auth_header(client, seed_users["kol"].email, "Creator@123")
    created = client.post(
        "/api/kol/bookings",
        headers=kol_headers,
        json={
            "scheduled_at": future_schedule.isoformat(),
            "pricing_type": "match",
            "quantity": 2,
            "guest_name": "Booking Tay",
            "guest_phone": "0909444555",
            "source": "external",
            "notes": "Khách chốt qua inbox",
        },
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    assert payload["source"] == "external"
    assert payload["customer_user_id"] is None
    assert payload["progress_percent"] == 0

    updated = client.patch(
        f"/api/kol/bookings/{payload['id']}/progress",
        headers=kol_headers,
        json={
            "progress_percent": 65,
            "progress_note": "Đã quay xong phần đầu",
            "extended_until": (future_schedule + timedelta(days=1)).isoformat(),
            "extension_note": "Brand xin dời deadline",
        },
    )
    assert updated.status_code == 200, updated.text
    updated_payload = updated.json()
    assert updated_payload["progress_percent"] == 65
    assert updated_payload["extension_count"] == 1
    assert updated_payload["extension_note"] == "Brand xin dời deadline"

    logs = client.get(f"/api/kol/bookings/{payload['id']}/logs", headers=kol_headers)
    assert logs.status_code == 200, logs.text
    rows = logs.json()
    assert len(rows) >= 2
    actions = [item["action"] for item in rows]
    assert "progress_updated" in actions
    assert "manual_booking_created" in actions


def test_customer_can_list_own_bookings(
    client: TestClient,
    seed_users: dict[str, User],
    future_schedule: datetime,
) -> None:
    created = client.post(
        "/api/bookings",
        headers=_auth_header(client, seed_users["customer"].email, "Customer@123"),
        json={
            "kol_user_id": str(seed_users["kol"].id),
            "scheduled_at": future_schedule.isoformat(),
            "pricing_type": "match",
            "quantity": 1,
            "notes": "Customer history booking",
        },
    )
    assert created.status_code == 201, created.text

    customer_headers = _auth_header(client, seed_users["customer"].email, "Customer@123")
    mine = client.get("/api/customer/bookings", headers=customer_headers)
    assert mine.status_code == 200
    rows = mine.json()
    assert len(rows) >= 1
    assert any(item["notes"] == "Customer history booking" for item in rows)
    assert all(item["customer_user_id"] == str(seed_users["customer"].id) for item in rows)


def test_profile_public_and_update(
    client: TestClient,
    seed_users: dict[str, User],
) -> None:
    public = client.get("/api/profiles/public/kol-test")
    assert public.status_code == 200
    assert public.json()["username"] == "kol-test"
    assert public.json()["price_per_match"] == 150000

    kol_headers = _auth_header(client, seed_users["kol"].email, "Creator@123")
    updated = client.put(
        f"/api/profiles/by-user/{seed_users['kol'].id}",
        headers=kol_headers,
        json={
            "display_name": "KOL Updated",
            "price_per_match": 200000,
            "bank_code": "970436",
            "bank_account_number": "0123456789",
            "bank_account_name": "KOL UPDATED",
            "bank_name": "Vietcombank (VCB)",
        },
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["display_name"] == "KOL Updated"
    assert updated.json()["price_per_match"] == 200000
