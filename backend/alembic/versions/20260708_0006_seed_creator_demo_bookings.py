"""seed many bookings for creator@example.com (creator-demo)

Revision ID: 20260708_0006
Revises: 20260708_0005
Create Date: 2026-07-08 20:40:00
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
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
BANK_DISPLAY = "MB Bank"

# Keep unit prices aligned with seeded creator pricing
PRICE_MATCH = 150000
PRICE_HOUR = 100000

BOOKING_IDS = [f"dddddddd-dddd-dddd-dddd-{str(i).zfill(12)}" for i in range(1, 31)]


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

    # Ensure creator pricing + bank stay usable for QR
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

    now = datetime.now(UTC)
    specs = [
        # upcoming / calendar heavy
        ("pending", "unpaid", "match", 2, 0, 10, CUSTOMER_DEMO, "Customer Demo", "0901000002", "Duo ranked tối nay"),
        ("pending", "unpaid", "hourly", 2, 0, 14, CUSTOMERS[0], "An Nguyễn", "0911000001", "Coach aim 2 giờ hôm nay"),
        ("confirmed", "paid", "match", 3, 0, 19, CUSTOMERS[1], "Bảo Trần", "0911000002", "3 trận Competitive đã chốt"),
        ("pending", "unpaid", "match", 1, 1, 9, None, "Guest Minh", "0987000111", "Khách vãng lai sáng mai"),
        ("confirmed", "paid", "hourly", 3, 1, 15, CUSTOMERS[2], "Chi Lê", "0911000003", "Collab content chiều mai"),
        ("pending", "unpaid", "hourly", 1, 1, 20, CUSTOMERS[3], "Dũng Phạm", "0911000004", "Review VOD tối mai"),
        ("confirmed", "paid", "match", 2, 2, 11, CUSTOMERS[4], "Em Võ", "0911000005", "2 trận custom room"),
        ("pending", "unpaid", "match", 4, 2, 16, CUSTOMER_DEMO, "Customer Demo", "0901000002", "Squad 4 trận cuối tuần"),
        ("confirmed", "unpaid", "hourly", 2, 3, 10, CUSTOMERS[0], "An Nguyễn", "0911000001", "Đã xác nhận nhưng chưa TT"),
        ("pending", "unpaid", "match", 1, 3, 18, None, "Guest Lan", "0908111222", "Đặt form công khai"),
        ("confirmed", "paid", "hourly", 4, 4, 13, CUSTOMERS[1], "Bảo Trần", "0911000002", "Marathon 4 giờ weekend"),
        ("pending", "unpaid", "match", 2, 5, 20, CUSTOMERS[2], "Chi Lê", "0911000003", "Night duo ranked"),
        ("confirmed", "paid", "match", 1, 6, 9, CUSTOMERS[3], "Dũng Phạm", "0911000004", "Warm-up sáng CN"),
        ("pending", "unpaid", "hourly", 2, 7, 15, CUSTOMERS[4], "Em Võ", "0911000005", "Coaching mid-week"),
        ("confirmed", "paid", "match", 3, 8, 17, CUSTOMER_DEMO, "Customer Demo", "0901000002", "Scrim 3 trận tuần sau"),
        ("pending", "unpaid", "hourly", 1, 9, 11, None, "Guest Khoa", "0933555666", "Trial 1 giờ"),
        ("confirmed", "paid", "match", 2, 10, 19, CUSTOMERS[0], "An Nguyễn", "0911000001", "Event collab đêm"),
        ("pending", "unpaid", "match", 1, 12, 14, CUSTOMERS[1], "Bảo Trần", "0911000002", "Booking xa hơn 12 ngày"),
        ("confirmed", "paid", "hourly", 3, 14, 16, CUSTOMERS[2], "Chi Lê", "0911000003", "Content shoot + live"),
        # history / reports
        ("completed", "paid", "match", 2, -1, 18, CUSTOMERS[3], "Dũng Phạm", "0911000004", "Hoàn thành hôm qua"),
        ("completed", "paid", "hourly", 2, -2, 15, CUSTOMERS[4], "Em Võ", "0911000005", "Coach xong 2 ngày trước"),
        ("cancelled", "unpaid", "match", 1, -2, 12, None, "Guest Hủy", "0977000888", "Khách hủy sát giờ"),
        ("completed", "paid", "match", 3, -3, 20, CUSTOMER_DEMO, "Customer Demo", "0901000002", "3 trận đã thu tiền"),
        ("completed", "paid", "hourly", 1, -4, 10, CUSTOMERS[0], "An Nguyễn", "0911000001", "Session sáng tuần trước"),
        ("cancelled", "unpaid", "hourly", 2, -5, 16, CUSTOMERS[1], "Bảo Trần", "0911000002", "Dời lịch / hủy"),
        ("completed", "paid", "match", 4, -6, 19, CUSTOMERS[2], "Chi Lê", "0911000003", "Squad weekend trước"),
        ("completed", "paid", "hourly", 3, -8, 14, CUSTOMERS[3], "Dũng Phạm", "0911000004", "Coaching dài 3 giờ"),
        ("completed", "paid", "match", 1, -10, 21, None, "Guest Tuấn", "0966123456", "Guest hoàn tất"),
        ("cancelled", "unpaid", "match", 2, -12, 9, CUSTOMERS[4], "Em Võ", "0911000005", "Hủy sớm"),
        ("completed", "paid", "hourly", 2, -15, 13, CUSTOMER_DEMO, "Customer Demo", "0901000002", "Report doanh thu tháng trước"),
    ]

    for index, spec in enumerate(specs, start=1):
        status, payment_status, pricing_type, quantity, day_offset, hour, customer_id, guest_name, guest_phone, notes = spec
        unit = PRICE_MATCH if pricing_type == "match" else PRICE_HOUR
        total = unit * quantity
        code = f"BKCREA{str(index).zfill(4)}"
        scheduled = (now + timedelta(days=day_offset)).replace(
            hour=hour % 24, minute=(index * 7) % 60, second=0, microsecond=0
        )
        qr = _vietqr(total, code, guest_name).replace("'", "''")
        customer_sql = f"'{customer_id}'::uuid" if customer_id else "NULL"
        notes_sql = notes.replace("'", "''")
        guest_sql = guest_name.replace("'", "''")
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
                    {customer_sql},
                    '{guest_sql}',
                    '{guest_phone}',
                    NULL,
                    NULL,
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
