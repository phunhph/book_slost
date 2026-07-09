"""seed customer bookings against creator-demo for client booking history

Revision ID: 20260708_0007
Revises: 20260708_0006
Create Date: 2026-07-08 20:50:00
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from urllib.parse import quote

from alembic import op
import sqlalchemy as sa


revision = "20260708_0007"
down_revision = "20260708_0006"
branch_labels = None
depends_on = None

KOL_ID = "22222222-2222-2222-2222-222222222222"
CUSTOMER_ID = "33333333-3333-3333-3333-333333333333"

PRICE_MATCH = 150000
PRICE_HOUR = 100000
BANK_CODE = "970422"
BANK_ACCOUNT = "0962954690"
BANK_NAME = "CREATOR DEMO"

BOOKING_IDS = [f"eeeeeeee-eeee-eeee-eeee-{str(i).zfill(12)}" for i in range(1, 13)]


def _vietqr(amount: int, code: str, guest: str) -> str:
    add_info = quote(f"{code} {guest}".strip(), safe="")
    name_q = quote(BANK_NAME, safe="")
    return (
        f"https://img.vietqr.io/image/{BANK_CODE}-{BANK_ACCOUNT}-compact2.png"
        f"?amount={amount}&addInfo={add_info}&accountName={name_q}"
    )


def upgrade() -> None:
    conn = op.get_bind()
    booking_list = ", ".join(f"'{bid}'::uuid" for bid in BOOKING_IDS)
    conn.execute(sa.text(f"DELETE FROM bookings WHERE id IN ({booking_list})"))

    # Keep customer profile contact filled for booking autofill checks
    conn.execute(
        sa.text(
            f"""
            UPDATE user_profiles
            SET display_name = COALESCE(display_name, 'Customer Demo'),
                phone = COALESCE(phone, '0901000002'),
                zalo = COALESCE(zalo, 'customer-demo'),
                messenger = COALESCE(messenger, 'customer.demo')
            WHERE user_id = '{CUSTOMER_ID}'::uuid
            """
        )
    )

    now = datetime.now(UTC)
    specs = [
        ("pending", "unpaid", "match", 2, 1, 10, "Khách đặt 2 trận với Creator Demo"),
        ("pending", "unpaid", "hourly", 1, 2, 15, "Coach 1 giờ cuối tuần"),
        ("confirmed", "paid", "match", 1, 3, 19, "Đã xác nhận + đã thanh toán QR"),
        ("confirmed", "unpaid", "hourly", 2, 4, 14, "Đã xác nhận nhưng chưa chuyển khoản"),
        ("pending", "unpaid", "match", 3, 5, 20, "Squad 3 trận tối"),
        ("confirmed", "paid", "hourly", 3, 7, 11, "Collab content 3 giờ"),
        ("completed", "paid", "match", 2, -1, 18, "Đã chơi xong hôm qua"),
        ("completed", "paid", "hourly", 2, -3, 16, "Coaching hoàn tất"),
        ("cancelled", "unpaid", "match", 1, -4, 12, "Khách hủy lịch"),
        ("completed", "paid", "match", 1, -6, 21, "Booking hoàn tất tuần trước"),
        ("pending", "unpaid", "hourly", 2, 10, 9, "Lịch xa để test calendar khách"),
        ("confirmed", "paid", "match", 4, 12, 17, "Event lớn 4 trận đã trả"),
    ]

    for index, spec in enumerate(specs, start=1):
        status, payment_status, pricing_type, quantity, day_offset, hour, notes = spec
        unit = PRICE_MATCH if pricing_type == "match" else PRICE_HOUR
        total = unit * quantity
        code = f"BKCUST{str(index).zfill(4)}"
        scheduled = (now + timedelta(days=day_offset)).replace(
            hour=hour % 24,
            minute=(index * 5) % 60,
            second=0,
            microsecond=0,
        )
        qr = _vietqr(total, code, "Customer Demo").replace("'", "''")
        notes_sql = notes.replace("'", "''")
        booking_id = BOOKING_IDS[index - 1]

        conn.execute(
            sa.text(
                f"""
                INSERT INTO bookings (
                    id, kol_user_id, customer_user_id,
                    guest_name, guest_phone, guest_zalo, guest_messenger,
                    scheduled_at, pricing_type, quantity, unit_price, total_amount, currency,
                    payment_qr_url, payment_code, payment_status, status, notes
                ) VALUES (
                    '{booking_id}'::uuid,
                    '{KOL_ID}'::uuid,
                    '{CUSTOMER_ID}'::uuid,
                    'Customer Demo',
                    '0901000002',
                    'customer-demo',
                    'customer.demo',
                    '{scheduled.isoformat()}'::timestamptz,
                    '{pricing_type}',
                    {quantity},
                    {unit},
                    {total},
                    'VND',
                    '{qr}',
                    '{code}',
                    '{payment_status}',
                    '{status}',
                    '{notes_sql}'
                )
                ON CONFLICT (id) DO NOTHING
                """
            )
        )


def downgrade() -> None:
    conn = op.get_bind()
    booking_list = ", ".join(f"'{bid}'::uuid" for bid in BOOKING_IDS)
    conn.execute(sa.text(f"DELETE FROM bookings WHERE id IN ({booking_list})"))
