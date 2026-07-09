"""seed many bookings for creator@example.com (creator-demo)

Revision ID: 20260708_0006
Revises: 20260708_0005
Create Date: 2026-07-08 20:40:00
"""

from __future__ import annotations

import random
import uuid
from datetime import UTC, datetime, timedelta, timezone
from urllib.parse import quote

from alembic import op
import sqlalchemy as sa


revision = "20260708_0006"
down_revision = "20260708_0005"
branch_labels = None
depends_on = None

KOL_ID = "22222222-2222-2222-2222-222222222222"
CUSTOMER_DEMO = "33333333-3333-3333-3333-333333333333"
CUSTOMERS = [
    "bbbbbbbb-bbbb-bbbb-bbbb-000000000001",
    "bbbbbbbb-bbbb-bbbb-bbbb-000000000002",
    "bbbbbbbb-bbbb-bbbb-bbbb-000000000003",
    "bbbbbbbb-bbbb-bbbb-bbbb-000000000004",
    "bbbbbbbb-bbbb-bbbb-bbbb-000000000005",
]

BANK_CODE = "970422"
BANK_ACCOUNT = "0962954690"
BANK_NAME = "CREATOR DEMO"

PRICE_MATCH = 150000
PRICE_HOUR = 100000


def _vietqr(amount: int, code: str, guest: str) -> str:
    add_info = quote(f"{code} {guest}".strip(), safe="")
    name_q = quote(BANK_NAME, safe="")
    return (
        f"https://img.vietqr.io/image/{BANK_CODE}-{BANK_ACCOUNT}-compact2.png"
        f"?amount={amount}&addInfo={add_info}&accountName={name_q}"
    )


def upgrade() -> None:
    conn = op.get_bind()
    
    # 1. Clear old bookings for the demo creator
    conn.execute(
        sa.text(f"DELETE FROM bookings WHERE kol_user_id = '{KOL_ID}'::uuid")
    )

    # Ensure creator pricing + bank details are active
    conn.execute(
        sa.text(
            f"""
            UPDATE user_profiles
            SET pricing_type = 'match',
                price_per_match = {PRICE_MATCH},
                price_per_hour = {PRICE_HOUR},
                currency = 'VND',
                bank_name = 'MB Bank',
                bank_code = '{BANK_CODE}',
                bank_account_number = '{BANK_ACCOUNT}',
                bank_account_name = '{BANK_NAME}'
            WHERE user_id = '{KOL_ID}'::uuid
            """
        )
    )

    # 2. Seed large dataset (2024 to 2026)
    now = datetime.now(timezone.utc)
    mock_guests = [
        ("Khánh Trần", "0912345678"),
        ("Bình Nguyễn", "0987654321"),
        ("Hải Đỗ", "0905556667"),
        ("Thanh Lê", "0977888999"),
        ("Duy Phạm", "0933444555"),
        ("Quỳnh Phan", "0966777888"),
        ("Nam Vũ", "0944111222"),
        ("Tú Hoàng", "0922333444"),
        ("Linh Đặng", "0988999000"),
        ("Sơn Ngô", "0955666777"),
    ]

    notes_pool = [
        "Duo ranked tối nay",
        "Coach aim 2 giờ hôm nay",
        "Giao lưu custom room",
        "Squad 4 trận cuối tuần",
        "Collab làm content Tiktok",
        "Review VOD đấu giải",
        "Marathon leo rank cuối tuần",
        "Training kỹ năng macro",
    ]

    # Use fixed seed for reproducible random outputs inside Alembic
    rng = random.Random(42)

    for year in [2024, 2025, 2026]:
        for month in range(1, 13):
            month_date = datetime(year, month, 15, tzinfo=timezone.utc)
            is_past = month_date < now.replace(day=15)
            is_present = (year == now.year and month == now.month)

            if year == 2024:
                num_bookings = rng.randint(6, 12)
            elif year == 2025:
                num_bookings = rng.randint(10, 18)
            else: # 2026
                num_bookings = rng.randint(12, 22)

            for idx in range(num_bookings):
                day = rng.randint(1, 28)
                hour = rng.randint(8, 22)
                minute = rng.randint(0, 59)
                scheduled_at = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)

                pricing_type = rng.choice(["match", "hourly"])
                quantity = rng.randint(1, 4)
                unit = PRICE_MATCH if pricing_type == "match" else PRICE_HOUR
                total = unit * quantity

                if is_past:
                    rand = rng.random()
                    if rand < 0.75:
                        status, payment_status = "completed", "paid"
                    elif rand < 0.90:
                        status, payment_status = "cancelled", "unpaid"
                    else:
                        status, payment_status = "confirmed", rng.choice(["paid", "unpaid"])
                elif is_present:
                    rand = rng.random()
                    if rand < 0.40:
                        status, payment_status = "completed", "paid"
                    elif rand < 0.70:
                        status, payment_status = "confirmed", rng.choice(["paid", "unpaid"])
                    elif rand < 0.85:
                        status, payment_status = "pending", "unpaid"
                    else:
                        status, payment_status = "cancelled", "unpaid"
                else:
                    rand = rng.random()
                    if rand < 0.60:
                        status, payment_status = "pending", "unpaid"
                    elif rand < 0.90:
                        status, payment_status = "confirmed", "unpaid"
                    else:
                        status, payment_status = "confirmed", "paid"

                if rng.random() < 0.3:
                    guest_name, guest_phone = rng.choice(mock_guests)
                    customer_sql = "NULL"
                else:
                    customer_user_id = rng.choice(CUSTOMERS + [CUSTOMER_DEMO])
                    customer_sql = f"'{customer_user_id}'::uuid"
                    guest_name = "Customer Demo" if customer_user_id == CUSTOMER_DEMO else f"Khách Hàng {str(customer_user_id)[:4]}"
                    guest_phone = f"0901{rng.randint(100000, 999999)}"

                bid = str(uuid.UUID(int=rng.getrandbits(128)))
                short_uuid = bid.replace("-", "")[:6].upper()
                code = f"BK{year % 100}{month:02d}{short_uuid}"
                qr = _vietqr(total, code, guest_name).replace("'", "''")
                notes_str = rng.choice(notes_pool).replace("'", "''")
                guest_str = guest_name.replace("'", "''")

                # set proof fields if paid
                proof_url = "'https://example.com/proofs/demo.png'" if payment_status == "paid" else "NULL"
                proof_note = "'Đã thanh toán chuyển khoản'" if payment_status == "paid" else "NULL"
                proof_time = f"'{ (scheduled_at - timedelta(minutes=rng.randint(5, 30))).isoformat() }'::timestamptz" if payment_status == "paid" else "NULL"
                review_time = f"'{ (scheduled_at + timedelta(minutes=rng.randint(1, 10))).isoformat() }'::timestamptz" if payment_status == "paid" else "NULL"
                progress_pct = 100 if status == "completed" else 0

                conn.execute(
                    sa.text(
                        f"""
                        INSERT INTO bookings (
                            id, kol_user_id, customer_user_id,
                            guest_name, guest_phone, scheduled_at,
                            pricing_type, quantity, unit_price, total_amount, currency,
                            payment_qr_url, payment_code, payment_status, status, notes,
                            payment_proof_url, payment_proof_note, payment_proof_uploaded_at, payment_reviewed_at,
                            progress_percent
                        ) VALUES (
                            '{bid}'::uuid,
                            '{KOL_ID}'::uuid,
                            {customer_sql},
                            '{guest_str}',
                            '{guest_phone}',
                            '{scheduled_at.isoformat()}'::timestamptz,
                            '{pricing_type}',
                            {quantity},
                            {unit},
                            {total},
                            'VND',
                            '{qr}',
                            '{code}',
                            '{payment_status}',
                            '{status}',
                            '{notes_str}',
                            {proof_url},
                            {proof_note},
                            {proof_time},
                            {review_time},
                            {progress_pct}
                        )
                        ON CONFLICT (id) DO NOTHING
                        """
                    )
                )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(f"DELETE FROM bookings WHERE kol_user_id = '{KOL_ID}'::uuid")
    )
