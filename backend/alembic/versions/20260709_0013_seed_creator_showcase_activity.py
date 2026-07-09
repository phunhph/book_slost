"""seed richer creator showcase bookings and activity logs

Revision ID: 20260709_0013
Revises: 20260709_0012
Create Date: 2026-07-09 15:15:00
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import json
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision = "20260709_0013"
down_revision = "20260709_0012"
branch_labels = None
depends_on = None

KOL_ID = "22222222-2222-2222-2222-222222222222"

SHOWCASE_BOOKINGS = [
    {
        "code": "BKCREA0001",
        "source": "system",
        "progress_percent": 10,
        "progress_note": "Đã nhận brief và chờ khách chốt concept quay.",
        "guest_zalo": "customer-demo",
        "guest_messenger": "customer.demo",
    },
    {
        "code": "BKCREA0002",
        "source": "external",
        "progress_percent": 55,
        "progress_note": "Đã xong buổi coaching đầu tiên, còn 1 buổi follow-up.",
        "guest_zalo": "annguyen.esports",
        "guest_messenger": "annguyen.esports",
    },
    {
        "code": "BKCREA0003",
        "source": "manual",
        "progress_percent": 100,
        "progress_note": "Đã giao nội dung và xác nhận hoàn tất.",
        "guest_zalo": "minh.guest",
        "guest_messenger": "minh.guest",
    },
    {
        "code": "BKCREA0004",
        "source": "external",
        "progress_percent": 20,
        "progress_note": "Khách để lại lead từ Facebook, đang chờ xác nhận cọc.",
        "guest_zalo": "guest-minh",
        "guest_messenger": "guest.minh.page",
    },
    {
        "code": "BKCREA0005",
        "source": "system",
        "progress_percent": 75,
        "progress_note": "Đã quay xong, đang chờ client duyệt caption cuối.",
        "extension_count": 1,
        "extension_note": "Brand xin dời lịch đăng 2 ngày.",
        "extend_days": 2,
        "guest_zalo": "chile.brand",
        "guest_messenger": "chile.brand",
    },
    {
        "code": "BKCREA0008",
        "source": "external",
        "progress_percent": 30,
        "progress_note": "Case chốt qua inbox, đã nhận outline sơ bộ.",
        "guest_zalo": "customer-demo",
    },
    {
        "code": "BKCREA0009",
        "source": "manual",
        "progress_percent": 65,
        "progress_note": "Đã confirm lịch nhưng khách chưa hoàn tất chuyển khoản.",
        "guest_zalo": "annguyen.esports",
    },
    {
        "code": "BKCREA0011",
        "source": "system",
        "progress_percent": 90,
        "progress_note": "Đang chờ đăng bài theo timeline cuối tuần.",
        "extension_count": 2,
        "extension_note": "Gia hạn thêm 1 buổi livestream bonus.",
        "extend_days": 3,
        "guest_zalo": "baotran.creator",
    },
    {
        "code": "BKCREA0015",
        "source": "system",
        "progress_percent": 35,
        "progress_note": "Đã chốt booking xa lịch, đang gom asset của brand.",
        "guest_zalo": "customer-demo",
    },
    {
        "code": "BKCREA0020",
        "source": "system",
        "progress_percent": 100,
        "progress_note": "Hoàn thành và đã đối soát đủ doanh thu.",
        "guest_zalo": "dungpham.final",
    },
    {
        "code": "BKCREA0022",
        "source": "external",
        "progress_percent": 0,
        "progress_note": "Khách hủy sát giờ, giữ lại để xem dashboard cancelled.",
        "guest_zalo": "guest-huy",
    },
]


def _insert_log(conn, booking_id: str, actor_user_id: str | None, actor_role: str | None, action: str, message: str, metadata: dict | None = None) -> None:
    conn.execute(
        sa.text(
            """
            INSERT INTO booking_activity_logs (
                id, booking_id, actor_user_id, actor_role, action, message, metadata_json
            ) VALUES (
                :id, :booking_id, :actor_user_id, :actor_role, :action, :message, :metadata_json
            )
            """
        ),
        {
            "id": str(uuid4()),
            "booking_id": booking_id,
            "actor_user_id": actor_user_id,
            "actor_role": actor_role,
            "action": action,
            "message": message,
            "metadata_json": json.dumps(metadata, ensure_ascii=False) if metadata else None,
        },
    )


def upgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            """
            SELECT id::text, payment_code, scheduled_at, guest_name, status, payment_status
            FROM bookings
            WHERE kol_user_id = CAST(:kol_id AS uuid)
            """
        ),
        {"kol_id": KOL_ID},
    ).mappings().all()

    by_code = {row["payment_code"]: row for row in rows if row["payment_code"]}
    conn.execute(
        sa.text(
            """
            DELETE FROM booking_activity_logs
            WHERE booking_id IN (
                SELECT id FROM bookings WHERE kol_user_id = CAST(:kol_id AS uuid)
            )
            """
        ),
        {"kol_id": KOL_ID},
    )

    now = datetime.now(UTC)
    for item in SHOWCASE_BOOKINGS:
        row = by_code.get(item["code"])
        if not row:
            continue

        scheduled_at = row["scheduled_at"]
        extended_until = None
        if item.get("extend_days"):
            extended_until = scheduled_at + timedelta(days=item["extend_days"])

        conn.execute(
            sa.text(
                """
                UPDATE bookings
                SET
                    source = :source,
                    progress_percent = :progress_percent,
                    progress_note = :progress_note,
                    extension_count = :extension_count,
                    extended_until = :extended_until,
                    extension_note = :extension_note,
                    progress_updated_at = :progress_updated_at,
                    guest_zalo = COALESCE(:guest_zalo, guest_zalo),
                    guest_messenger = COALESCE(:guest_messenger, guest_messenger)
                WHERE id = CAST(:booking_id AS uuid)
                """
            ),
            {
                "source": item["source"],
                "progress_percent": item["progress_percent"],
                "progress_note": item["progress_note"],
                "extension_count": item.get("extension_count", 0),
                "extended_until": extended_until,
                "extension_note": item.get("extension_note"),
                "progress_updated_at": now,
                "guest_zalo": item.get("guest_zalo"),
                "guest_messenger": item.get("guest_messenger"),
                "booking_id": row["id"],
            },
        )

        _insert_log(
            conn,
            booking_id=row["id"],
            actor_user_id=KOL_ID,
            actor_role="kol",
            action="seed_showcase_created",
            message=f"Seed showcase cho {row['guest_name']} để demo dashboard/booking/profile.",
            metadata={
                "payment_code": item["code"],
                "source": item["source"],
                "status": row["status"],
                "payment_status": row["payment_status"],
            },
        )
        _insert_log(
            conn,
            booking_id=row["id"],
            actor_user_id=KOL_ID,
            actor_role="kol",
            action="progress_updated",
            message="Seed tiến độ để màn booking detail và reports có dữ liệu phong phú.",
            metadata={
                "progress_percent": item["progress_percent"],
                "progress_note": item["progress_note"],
                "extended_until": extended_until.isoformat() if extended_until else None,
                "extension_count": item.get("extension_count", 0),
                "extension_note": item.get("extension_note"),
            },
        )
        if item["source"] in {"manual", "external"}:
            _insert_log(
                conn,
                booking_id=row["id"],
                actor_user_id=KOL_ID,
                actor_role="kol",
                action="manual_booking_created",
                message="Seed case booking ngoài hệ thống / tạo tay để demo luồng vận hành.",
                metadata={"source": item["source"], "payment_code": item["code"]},
            )
        if row["payment_status"] == "paid":
            _insert_log(
                conn,
                booking_id=row["id"],
                actor_user_id=KOL_ID,
                actor_role="kol",
                action="payment_reviewed",
                message="Seed trạng thái đã duyệt thanh toán cho case demo.",
                metadata={"action": "approve", "payment_status": "paid"},
            )
        elif row["payment_status"] == "unpaid" and row["status"] in {"pending", "confirmed"}:
            _insert_log(
                conn,
                booking_id=row["id"],
                actor_user_id=None,
                actor_role="system",
                action="followup_needed",
                message="Seed nhắc theo dõi thanh toán / chốt lịch cho case đang mở.",
                metadata={"status": row["status"], "payment_status": row["payment_status"]},
            )


def downgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            """
            SELECT id::text
            FROM bookings
            WHERE kol_user_id = CAST(:kol_id AS uuid)
            """
        ),
        {"kol_id": KOL_ID},
    ).mappings().all()
    conn.execute(
        sa.text(
            """
            DELETE FROM booking_activity_logs
            WHERE booking_id IN (
                SELECT id FROM bookings WHERE kol_user_id = CAST(:kol_id AS uuid)
            )
            """
        ),
        {"kol_id": KOL_ID},
    )
