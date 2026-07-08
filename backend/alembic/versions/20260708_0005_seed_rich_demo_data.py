"""seed many kols, customers and varied bookings

Revision ID: 20260708_0005
Revises: 20260708_0004
Create Date: 2026-07-08 19:50:00
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from urllib.parse import quote

from alembic import op
import sqlalchemy as sa


revision = "20260708_0005"
down_revision = "20260708_0004"
branch_labels = None
depends_on = None

# Reuse bcrypt hashes from role seed (Creator@123 / Customer@123)
KOL_PASSWORD_HASH = "$2b$12$jLYxxX1bYkwjk4Zs7kosmu8nCazEqfKuofHYdjKcH32xNQ5vlS.qy"
CUSTOMER_PASSWORD_HASH = "$2b$12$X.memEy2102dEKo0Ilb3K.pfd3Mk95fy12aR8Hq4pYQgLdAI7aw3O"

EXISTING_KOL_ID = "22222222-2222-2222-2222-222222222222"
EXISTING_CUSTOMER_ID = "33333333-3333-3333-3333-333333333333"

DEFAULT_LAYOUT = {
    "version": 2,
    "blocks": [
        {"id": "hero", "type": "hero", "active": True, "order": 0, "data": {}},
        {
            "id": "about",
            "type": "about",
            "active": True,
            "order": 1,
            "data": {"content": "KOL game / content creator nhận booking chơi cùng và collab."},
        },
        {
            "id": "booking",
            "type": "booking",
            "active": True,
            "order": 2,
            "data": {
                "title": "Đặt lịch chơi cùng",
                "subtitle": "Chọn theo trận hoặc theo giờ, thanh toán qua VietQR.",
            },
        },
        {
            "id": "contact",
            "type": "contact",
            "active": True,
            "order": 3,
            "data": {},
        },
    ],
}

# 8 extra KOLs (existing creator-demo stays as main)
KOLS = [
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-000000000001",
        "email": "luna.fps@example.com",
        "username": "luna-fps",
        "display_name": "Luna FPS",
        "bio": "Main Valorant / CS2. Nhận duo ranked và scrim theo trận.",
        "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=500&q=80",
        "primary_color": "#EF4444",
        "text_color": "#F8FAFC",
        "bg_type": "gradient",
        "bg_value": "linear-gradient(135deg, #450a0a 0%, #0f172a 100%)",
        "phone": "0902000001",
        "zalo": "luna-fps",
        "messenger": "luna.fps",
        "pricing_type": "match",
        "price_per_match": 180000,
        "price_per_hour": 120000,
        "bank_name": "Vietcombank (VCB)",
        "bank_code": "970436",
        "bank_account_number": "1011222333",
        "bank_account_name": "NGUYEN LUNA",
    },
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-000000000002",
        "email": "kai.moba@example.com",
        "username": "kai-moba",
        "display_name": "Kai MOBA",
        "bio": "Liên Quân / Wild Rift coach. Booking theo giờ coaching.",
        "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=500&q=80",
        "primary_color": "#8B5CF6",
        "text_color": "#F8FAFC",
        "bg_type": "gradient",
        "bg_value": "linear-gradient(135deg, #2e1065 0%, #0f172a 100%)",
        "phone": "0902000002",
        "zalo": "kai-moba",
        "messenger": "kai.moba",
        "pricing_type": "hourly",
        "price_per_match": 100000,
        "price_per_hour": 150000,
        "bank_name": "Techcombank",
        "bank_code": "970407",
        "bank_account_number": "1903344556",
        "bank_account_name": "TRAN KAI",
    },
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-000000000003",
        "email": "mira.stream@example.com",
        "username": "mira-stream",
        "display_name": "Mira Stream",
        "bio": "Streamer Just Chatting + co-op. Nhận collab content và chơi cùng.",
        "avatar_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=500&q=80",
        "primary_color": "#EC4899",
        "text_color": "#111111",
        "bg_type": "gradient",
        "bg_value": "linear-gradient(135deg, #fdf2f8 0%, #ede9fe 100%)",
        "phone": "0902000003",
        "zalo": "mira-stream",
        "messenger": "mira.stream",
        "pricing_type": "hourly",
        "price_per_match": 200000,
        "price_per_hour": 175000,
        "bank_name": "MB Bank",
        "bank_code": "970422",
        "bank_account_number": "0888123456",
        "bank_account_name": "LE MIRA",
    },
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-000000000004",
        "email": "rex.pubg@example.com",
        "username": "rex-pubg",
        "display_name": "Rex PUBG",
        "bio": "PUBG Mobile / BGMI. Duo / squad theo trận.",
        "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=500&q=80",
        "primary_color": "#F59E0B",
        "text_color": "#0F172A",
        "bg_type": "color",
        "bg_value": "#FFFBEB",
        "phone": "0902000004",
        "zalo": "rex-pubg",
        "messenger": "rex.pubg",
        "pricing_type": "match",
        "price_per_match": 120000,
        "price_per_hour": 90000,
        "bank_name": "BIDV",
        "bank_code": "970418",
        "bank_account_number": "2155667788",
        "bank_account_name": "PHAM REX",
    },
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-000000000005",
        "email": "nova.tft@example.com",
        "username": "nova-tft",
        "display_name": "Nova TFT",
        "bio": "TFT Challenger. Review composition và coaching theo giờ.",
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=500&q=80",
        "primary_color": "#06B6D4",
        "text_color": "#F8FAFC",
        "bg_type": "gradient",
        "bg_value": "linear-gradient(135deg, #083344 0%, #0f172a 100%)",
        "phone": "0902000005",
        "zalo": "nova-tft",
        "messenger": "nova.tft",
        "pricing_type": "hourly",
        "price_per_match": 80000,
        "price_per_hour": 130000,
        "bank_name": "VPBank",
        "bank_code": "970432",
        "bank_account_number": "9876543210",
        "bank_account_name": "VO NOVA",
    },
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-000000000006",
        "email": "ash.genshin@example.com",
        "username": "ash-genshin",
        "display_name": "Ash Genshin",
        "bio": "Genshin / HSR co-op, farm và show builds. Booking theo giờ.",
        "avatar_url": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?auto=format&fit=crop&w=500&q=80",
        "primary_color": "#22C55E",
        "text_color": "#052E16",
        "bg_type": "color",
        "bg_value": "#F0FDF4",
        "phone": "0902000006",
        "zalo": "ash-genshin",
        "messenger": "ash.genshin",
        "pricing_type": "hourly",
        "price_per_match": 90000,
        "price_per_hour": 110000,
        "bank_name": "TPBank",
        "bank_code": "970423",
        "bank_account_number": "0001122334",
        "bank_account_name": "DO ASH",
    },
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-000000000007",
        "email": "bolt.fc@example.com",
        "username": "bolt-fc",
        "display_name": "Bolt FC",
        "bio": "FC Online / FIFA. Nhận thách đấu và coaching skill move.",
        "avatar_url": "https://images.unsplash.com/photo-1566492031773-bb5ecba01fbc?auto=format&fit=crop&w=500&q=80",
        "primary_color": "#3B82F6",
        "text_color": "#F8FAFC",
        "bg_type": "gradient",
        "bg_value": "linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%)",
        "phone": "0902000007",
        "zalo": "bolt-fc",
        "messenger": "bolt.fc",
        "pricing_type": "match",
        "price_per_match": 150000,
        "price_per_hour": 100000,
        "bank_name": "VietinBank",
        "bank_code": "970415",
        "bank_account_number": "1099887766",
        "bank_account_name": "HOANG BOLT",
    },
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-000000000008",
        "email": "ivy.roblox@example.com",
        "username": "ivy-roblox",
        "display_name": "Ivy Roblox",
        "bio": "Roblox / Minecraft builder. Session chơi cùng cho nhóm.",
        "avatar_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=500&q=80",
        "primary_color": "#A855F7",
        "text_color": "#F8FAFC",
        "bg_type": "gradient",
        "bg_value": "linear-gradient(135deg, #581c87 0%, #312e81 100%)",
        "phone": "0902000008",
        "zalo": "ivy-roblox",
        "messenger": "ivy.roblox",
        "pricing_type": "hourly",
        "price_per_match": 70000,
        "price_per_hour": 95000,
        "bank_name": "Sacombank",
        "bank_code": "970403",
        "bank_account_number": "0601234567",
        "bank_account_name": "BUI IVY",
    },
]

# 5 extra customers (existing customer-demo stays)
CUSTOMERS = [
    {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-000000000001",
        "email": "an.nguyen@example.com",
        "username": "an-nguyen",
        "display_name": "An Nguyễn",
        "phone": "0911000001",
        "zalo": "an.nguyen",
        "messenger": "an.nguyen",
    },
    {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-000000000002",
        "email": "bao.tran@example.com",
        "username": "bao-tran",
        "display_name": "Bảo Trần",
        "phone": "0911000002",
        "zalo": "bao.tran",
        "messenger": "bao.tran",
    },
    {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-000000000003",
        "email": "chi.le@example.com",
        "username": "chi-le",
        "display_name": "Chi Lê",
        "phone": "0911000003",
        "zalo": "chi.le",
        "messenger": "chi.le",
    },
    {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-000000000004",
        "email": "dung.pham@example.com",
        "username": "dung-pham",
        "display_name": "Dũng Phạm",
        "phone": "0911000004",
        "zalo": "dung.pham",
        "messenger": "dung.pham",
    },
    {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-000000000005",
        "email": "em.vo@example.com",
        "username": "em-vo",
        "display_name": "Em Võ",
        "phone": "0911000005",
        "zalo": "em.vo",
        "messenger": "em.vo",
    },
]

SEED_USER_IDS = [k["id"] for k in KOLS] + [c["id"] for c in CUSTOMERS]
SEED_BOOKING_IDS = [f"cccccccc-cccc-cccc-cccc-{str(i).zfill(12)}" for i in range(1, 21)]
SEED_BOOKING_IDS.append("cccccccc-cccc-cccc-cccc-000000000021")
SEED_BOOKING_IDS.append("cccccccc-cccc-cccc-cccc-000000000022")


def _vietqr(bank_code: str, account_number: str, account_name: str, amount: int, code: str, guest: str) -> str:
    add_info = quote(f"{code} {guest}".strip(), safe="")
    name_q = quote(account_name, safe="")
    return (
        f"https://img.vietqr.io/image/{bank_code}-{account_number}-compact2.png"
        f"?amount={amount}&addInfo={add_info}&accountName={name_q}"
    )


def _layout_for(kol: dict) -> dict:
    layout = json.loads(json.dumps(DEFAULT_LAYOUT))
    layout["blocks"][1]["data"]["content"] = (
        f"Xin chào, mình là {kol['display_name']}.\n\n{kol['bio']}\n\n"
        "Đặt lịch bên dưới để chơi cùng hoặc collab."
    )
    layout["blocks"][3]["data"] = {
        "phone": kol["phone"],
        "zalo": kol["zalo"],
        "messenger": kol["messenger"],
    }
    return layout


def upgrade() -> None:
    conn = op.get_bind()
    layout_json = json.dumps(DEFAULT_LAYOUT, ensure_ascii=False).replace("'", "''")

    # Clean previous run of this seed (idempotent-ish)
    id_list = ", ".join(f"'{uid}'::uuid" for uid in SEED_USER_IDS)
    booking_list = ", ".join(f"'{bid}'::uuid" for bid in SEED_BOOKING_IDS)
    conn.execute(sa.text(f"DELETE FROM bookings WHERE id IN ({booking_list})"))
    conn.execute(sa.text(f"DELETE FROM user_profiles WHERE user_id IN ({id_list})"))
    conn.execute(sa.text(f"DELETE FROM users WHERE id IN ({id_list})"))

    for kol in KOLS:
        layout = json.dumps(_layout_for(kol), ensure_ascii=False).replace("'", "''")
        conn.execute(
            sa.text(
                f"""
                INSERT INTO users (id, email, password_hash, auth_provider, role, is_active)
                VALUES (
                    '{kol["id"]}'::uuid,
                    '{kol["email"]}',
                    '{KOL_PASSWORD_HASH}',
                    'local',
                    'kol',
                    true
                )
                ON CONFLICT (id) DO NOTHING
                """
            )
        )
        conn.execute(
            sa.text(
                f"""
                INSERT INTO user_profiles (
                    user_id, username, display_name, bio, avatar_url,
                    theme_mode, font_family, primary_color, text_color,
                    bg_type, bg_value, avatar_style, button_style,
                    phone, zalo, messenger,
                    pricing_type, price_per_match, price_per_hour, currency,
                    bank_name, bank_code, bank_account_number, bank_account_name,
                    layout_structure
                ) VALUES (
                    '{kol["id"]}'::uuid,
                    '{kol["username"]}',
                    '{kol["display_name"]}',
                    '{kol["bio"].replace("'", "''")}',
                    '{kol["avatar_url"]}',
                    'dark',
                    'Be Vietnam Pro',
                    '{kol["primary_color"]}',
                    '{kol["text_color"]}',
                    '{kol["bg_type"]}',
                    '{kol["bg_value"]}',
                    'rounded',
                    'filled',
                    '{kol["phone"]}',
                    '{kol["zalo"]}',
                    '{kol["messenger"]}',
                    '{kol["pricing_type"]}',
                    {kol["price_per_match"]},
                    {kol["price_per_hour"]},
                    'VND',
                    '{kol["bank_name"]}',
                    '{kol["bank_code"]}',
                    '{kol["bank_account_number"]}',
                    '{kol["bank_account_name"]}',
                    '{layout}'::jsonb
                )
                ON CONFLICT (user_id) DO NOTHING
                """
            )
        )

    for customer in CUSTOMERS:
        conn.execute(
            sa.text(
                f"""
                INSERT INTO users (id, email, password_hash, auth_provider, role, is_active)
                VALUES (
                    '{customer["id"]}'::uuid,
                    '{customer["email"]}',
                    '{CUSTOMER_PASSWORD_HASH}',
                    'local',
                    'customer',
                    true
                )
                ON CONFLICT (id) DO NOTHING
                """
            )
        )
        conn.execute(
            sa.text(
                f"""
                INSERT INTO user_profiles (
                    user_id, username, display_name, bio, avatar_url,
                    theme_mode, font_family, primary_color, text_color,
                    bg_type, bg_value, avatar_style, button_style,
                    phone, zalo, messenger,
                    pricing_type, price_per_match, price_per_hour, currency,
                    layout_structure
                ) VALUES (
                    '{customer["id"]}'::uuid,
                    '{customer["username"]}',
                    '{customer["display_name"]}',
                    'Khách demo đặt lịch chơi cùng KOL.',
                    NULL,
                    'light',
                    'Inter',
                    '#2563EB',
                    '#111111',
                    'color',
                    '#EFF6FF',
                    'circle',
                    'outline',
                    '{customer["phone"]}',
                    '{customer["zalo"]}',
                    '{customer["messenger"]}',
                    'match',
                    0,
                    0,
                    'VND',
                    '{layout_json}'::jsonb
                )
                ON CONFLICT (user_id) DO NOTHING
                """
            )
        )

    now = datetime.now(UTC)
    kol_by_id = {k["id"]: k for k in KOLS}
    kol_by_id[EXISTING_KOL_ID] = {
        "id": EXISTING_KOL_ID,
        "bank_code": "970436",
        "bank_account_number": "0123456789",
        "bank_account_name": "CREATOR DEMO",
        "bank_name": "Vietcombank",
        "price_per_match": 150000,
        "price_per_hour": 100000,
    }

    bookings = [
        # creator-demo mix
        {
            "id": SEED_BOOKING_IDS[0],
            "kol_id": EXISTING_KOL_ID,
            "customer_id": EXISTING_CUSTOMER_ID,
            "guest_name": "Customer Demo",
            "guest_phone": "0901000002",
            "days": 1,
            "status": "pending",
            "pricing_type": "match",
            "quantity": 2,
            "payment_status": "unpaid",
            "notes": "Duo ranked Valorant, rank Gold.",
        },
        {
            "id": SEED_BOOKING_IDS[1],
            "kol_id": EXISTING_KOL_ID,
            "customer_id": CUSTOMERS[0]["id"],
            "guest_name": CUSTOMERS[0]["display_name"],
            "guest_phone": CUSTOMERS[0]["phone"],
            "days": 3,
            "status": "confirmed",
            "pricing_type": "hourly",
            "quantity": 2,
            "payment_status": "paid",
            "notes": "Coaching 2 giờ tối thứ 6.",
        },
        {
            "id": SEED_BOOKING_IDS[2],
            "kol_id": EXISTING_KOL_ID,
            "customer_id": None,
            "guest_name": "Khách vãng lai Minh",
            "guest_phone": "0987654321",
            "days": -2,
            "status": "completed",
            "pricing_type": "match",
            "quantity": 1,
            "payment_status": "paid",
            "notes": "Đã chơi xong 1 trận.",
        },
        {
            "id": SEED_BOOKING_IDS[3],
            "kol_id": EXISTING_KOL_ID,
            "customer_id": CUSTOMERS[1]["id"],
            "guest_name": CUSTOMERS[1]["display_name"],
            "guest_phone": CUSTOMERS[1]["phone"],
            "days": -5,
            "status": "cancelled",
            "pricing_type": "hourly",
            "quantity": 1,
            "payment_status": "unpaid",
            "notes": "Khách hủy vì bận.",
        },
        # luna-fps
        {
            "id": SEED_BOOKING_IDS[4],
            "kol_id": KOLS[0]["id"],
            "customer_id": CUSTOMERS[0]["id"],
            "guest_name": CUSTOMERS[0]["display_name"],
            "guest_phone": CUSTOMERS[0]["phone"],
            "days": 2,
            "status": "pending",
            "pricing_type": "match",
            "quantity": 3,
            "payment_status": "unpaid",
            "notes": "3 trận Valorant Competitive.",
        },
        {
            "id": SEED_BOOKING_IDS[5],
            "kol_id": KOLS[0]["id"],
            "customer_id": CUSTOMERS[2]["id"],
            "guest_name": CUSTOMERS[2]["display_name"],
            "guest_phone": CUSTOMERS[2]["phone"],
            "days": 4,
            "status": "confirmed",
            "pricing_type": "hourly",
            "quantity": 1,
            "payment_status": "paid",
            "notes": "Aim training 1 giờ.",
        },
        # kai-moba
        {
            "id": SEED_BOOKING_IDS[6],
            "kol_id": KOLS[1]["id"],
            "customer_id": CUSTOMERS[1]["id"],
            "guest_name": CUSTOMERS[1]["display_name"],
            "guest_phone": CUSTOMERS[1]["phone"],
            "days": 1,
            "status": "pending",
            "pricing_type": "hourly",
            "quantity": 2,
            "payment_status": "unpaid",
            "notes": "Coach Liên Quân mid lane.",
        },
        {
            "id": SEED_BOOKING_IDS[7],
            "kol_id": KOLS[1]["id"],
            "customer_id": None,
            "guest_name": "Guest Khoa",
            "guest_phone": "0903111222",
            "days": -1,
            "status": "completed",
            "pricing_type": "match",
            "quantity": 2,
            "payment_status": "paid",
            "notes": "2 trận ranked night.",
        },
        # mira-stream
        {
            "id": SEED_BOOKING_IDS[8],
            "kol_id": KOLS[2]["id"],
            "customer_id": CUSTOMERS[3]["id"],
            "guest_name": CUSTOMERS[3]["display_name"],
            "guest_phone": CUSTOMERS[3]["phone"],
            "days": 5,
            "status": "confirmed",
            "pricing_type": "hourly",
            "quantity": 3,
            "payment_status": "paid",
            "notes": "Collab stream co-op 3 giờ.",
        },
        {
            "id": SEED_BOOKING_IDS[9],
            "kol_id": KOLS[2]["id"],
            "customer_id": CUSTOMERS[4]["id"],
            "guest_name": CUSTOMERS[4]["display_name"],
            "guest_phone": CUSTOMERS[4]["phone"],
            "days": 0,
            "status": "pending",
            "pricing_type": "match",
            "quantity": 1,
            "payment_status": "unpaid",
            "notes": "Chơi thử game mới.",
        },
        # rex-pubg
        {
            "id": SEED_BOOKING_IDS[10],
            "kol_id": KOLS[3]["id"],
            "customer_id": CUSTOMERS[0]["id"],
            "guest_name": CUSTOMERS[0]["display_name"],
            "guest_phone": CUSTOMERS[0]["phone"],
            "days": 2,
            "status": "confirmed",
            "pricing_type": "match",
            "quantity": 4,
            "payment_status": "paid",
            "notes": "Squad 4 trận classic.",
        },
        {
            "id": SEED_BOOKING_IDS[11],
            "kol_id": KOLS[3]["id"],
            "customer_id": None,
            "guest_name": "Tuấn Guest",
            "guest_phone": "0933444555",
            "days": -3,
            "status": "cancelled",
            "pricing_type": "hourly",
            "quantity": 2,
            "payment_status": "unpaid",
            "notes": "Hủy do mất mạng.",
        },
        # nova-tft
        {
            "id": SEED_BOOKING_IDS[12],
            "kol_id": KOLS[4]["id"],
            "customer_id": CUSTOMERS[2]["id"],
            "guest_name": CUSTOMERS[2]["display_name"],
            "guest_phone": CUSTOMERS[2]["phone"],
            "days": 6,
            "status": "pending",
            "pricing_type": "hourly",
            "quantity": 1,
            "payment_status": "unpaid",
            "notes": "Review team comp mới.",
        },
        {
            "id": SEED_BOOKING_IDS[13],
            "kol_id": KOLS[4]["id"],
            "customer_id": EXISTING_CUSTOMER_ID,
            "guest_name": "Customer Demo",
            "guest_phone": "0901000002",
            "days": -4,
            "status": "completed",
            "pricing_type": "hourly",
            "quantity": 2,
            "payment_status": "paid",
            "notes": "Coaching climb rank.",
        },
        # ash-genshin
        {
            "id": SEED_BOOKING_IDS[14],
            "kol_id": KOLS[5]["id"],
            "customer_id": CUSTOMERS[1]["id"],
            "guest_name": CUSTOMERS[1]["display_name"],
            "guest_phone": CUSTOMERS[1]["phone"],
            "days": 3,
            "status": "confirmed",
            "pricing_type": "hourly",
            "quantity": 2,
            "payment_status": "paid",
            "notes": "Farm domain + abyss.",
        },
        {
            "id": SEED_BOOKING_IDS[15],
            "kol_id": KOLS[5]["id"],
            "customer_id": CUSTOMERS[3]["id"],
            "guest_name": CUSTOMERS[3]["display_name"],
            "guest_phone": CUSTOMERS[3]["phone"],
            "days": 7,
            "status": "pending",
            "pricing_type": "match",
            "quantity": 1,
            "payment_status": "unpaid",
            "notes": "Event limited co-op.",
        },
        # bolt-fc
        {
            "id": SEED_BOOKING_IDS[16],
            "kol_id": KOLS[6]["id"],
            "customer_id": CUSTOMERS[4]["id"],
            "guest_name": CUSTOMERS[4]["display_name"],
            "guest_phone": CUSTOMERS[4]["phone"],
            "days": 1,
            "status": "pending",
            "pricing_type": "match",
            "quantity": 2,
            "payment_status": "unpaid",
            "notes": "Thách đấu Division Rivals.",
        },
        {
            "id": SEED_BOOKING_IDS[17],
            "kol_id": KOLS[6]["id"],
            "customer_id": None,
            "guest_name": "Huy FC",
            "guest_phone": "0977000111",
            "days": -6,
            "status": "completed",
            "pricing_type": "match",
            "quantity": 3,
            "payment_status": "paid",
            "notes": "3 trận đã xong.",
        },
        # ivy-roblox
        {
            "id": SEED_BOOKING_IDS[18],
            "kol_id": KOLS[7]["id"],
            "customer_id": CUSTOMERS[0]["id"],
            "guest_name": CUSTOMERS[0]["display_name"],
            "guest_phone": CUSTOMERS[0]["phone"],
            "days": 2,
            "status": "confirmed",
            "pricing_type": "hourly",
            "quantity": 2,
            "payment_status": "paid",
            "notes": "Build server Minecraft với nhóm.",
        },
        {
            "id": SEED_BOOKING_IDS[19],
            "kol_id": KOLS[7]["id"],
            "customer_id": CUSTOMERS[2]["id"],
            "guest_name": CUSTOMERS[2]["display_name"],
            "guest_phone": CUSTOMERS[2]["phone"],
            "days": -1,
            "status": "cancelled",
            "pricing_type": "hourly",
            "quantity": 1,
            "payment_status": "unpaid",
            "notes": "Dời lịch sang tuần sau.",
        },
        # extra pending guests
        {
            "id": SEED_BOOKING_IDS[20],
            "kol_id": KOLS[0]["id"],
            "customer_id": None,
            "guest_name": "Lan Guest",
            "guest_phone": "0908888777",
            "days": 8,
            "status": "pending",
            "pricing_type": "match",
            "quantity": 1,
            "payment_status": "unpaid",
            "notes": "Đặt qua form công khai.",
        },
        {
            "id": SEED_BOOKING_IDS[21],
            "kol_id": KOLS[2]["id"],
            "customer_id": CUSTOMERS[1]["id"],
            "guest_name": CUSTOMERS[1]["display_name"],
            "guest_phone": CUSTOMERS[1]["phone"],
            "days": -8,
            "status": "completed",
            "pricing_type": "hourly",
            "quantity": 4,
            "payment_status": "paid",
            "notes": "Marathon collab weekend.",
        },
    ]

    for index, booking in enumerate(bookings, start=1):
        kol = kol_by_id[booking["kol_id"]]
        unit = (
            kol["price_per_match"]
            if booking["pricing_type"] == "match"
            else kol["price_per_hour"]
        )
        quantity = booking["quantity"]
        total = unit * quantity
        code = f"BKSEED{str(index).zfill(4)}"
        scheduled = (now + timedelta(days=booking["days"], hours=index % 5)).isoformat()
        qr = _vietqr(
            kol["bank_code"],
            kol["bank_account_number"],
            kol["bank_account_name"],
            total,
            code,
            booking["guest_name"],
        ).replace("'", "''")
        customer_sql = f"'{booking['customer_id']}'::uuid" if booking["customer_id"] else "NULL"
        notes = booking["notes"].replace("'", "''")
        guest_name = booking["guest_name"].replace("'", "''")

        conn.execute(
            sa.text(
                f"""
                INSERT INTO bookings (
                    id, kol_user_id, customer_user_id,
                    guest_name, guest_phone, guest_zalo, guest_messenger,
                    scheduled_at, pricing_type, quantity, unit_price, total_amount, currency,
                    payment_qr_url, payment_code, payment_status, status, notes
                ) VALUES (
                    '{booking["id"]}'::uuid,
                    '{booking["kol_id"]}'::uuid,
                    {customer_sql},
                    '{guest_name}',
                    '{booking["guest_phone"]}',
                    NULL,
                    NULL,
                    '{scheduled}'::timestamptz,
                    '{booking["pricing_type"]}',
                    {quantity},
                    {unit},
                    {total},
                    'VND',
                    '{qr}',
                    '{code}',
                    '{booking["payment_status"]}',
                    '{booking["status"]}',
                    '{notes}'
                )
                ON CONFLICT (id) DO NOTHING
                """
            )
        )


def downgrade() -> None:
    conn = op.get_bind()
    id_list = ", ".join(f"'{uid}'::uuid" for uid in SEED_USER_IDS)
    booking_list = ", ".join(f"'{bid}'::uuid" for bid in SEED_BOOKING_IDS)
    conn.execute(sa.text(f"DELETE FROM bookings WHERE id IN ({booking_list})"))
    conn.execute(sa.text(f"DELETE FROM user_profiles WHERE user_id IN ({id_list})"))
    conn.execute(sa.text(f"DELETE FROM users WHERE id IN ({id_list})"))
