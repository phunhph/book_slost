"""Seed rich demo content for creator-demo public profile."""

from __future__ import annotations

import json

from alembic import op
import sqlalchemy as sa

revision = "20260708_0002"
down_revision = "20260708_0001"
branch_labels = None
depends_on = None

KOL_USER_ID = "22222222-2222-2222-2222-222222222222"

CREATOR_DEMO_LAYOUT = {
    "version": 2,
    "blocks": [
        {"id": "hero", "type": "hero", "active": True, "order": 0, "data": {}},
        {
            "id": "about-demo",
            "type": "about",
            "active": True,
            "order": 1,
            "data": {
                "content": (
                    "Xin chào, mình là Creator Demo — KOL chuyên lifestyle, review sản phẩm và storytelling ngắn.\n\n"
                    "• 120K+ followers trên TikTok & Instagram\n"
                    "• Tỷ lệ engagement trung bình 6.8%\n"
                    "• Đã hợp tác với 30+ thương hiệu trong nước\n\n"
                    "Mình nhận booking review, livestream, UGC và chiến dịch dài hạn. Hãy để lại brief qua form bên dưới nhé!"
                )
            },
        },
        {
            "id": "social-demo",
            "type": "social_links",
            "active": True,
            "order": 2,
            "data": {
                "items": [
                    {"platform": "instagram", "label": "Instagram", "url": "https://instagram.com/creator.demo"},
                    {"platform": "tiktok", "label": "TikTok", "url": "https://tiktok.com/@creatordemo"},
                    {"platform": "youtube", "label": "YouTube", "url": "https://youtube.com/@creatordemo"},
                    {"platform": "website", "label": "Website", "url": "https://slost.app"},
                ]
            },
        },
        {
            "id": "gallery-demo",
            "type": "gallery",
            "active": True,
            "order": 3,
            "data": {
                "layout": "grid",
                "items": [
                    {
                        "url": "https://images.unsplash.com/photo-1611162617474-5b21e039e566?auto=format&fit=crop&w=900&q=80",
                        "alt": "Social content",
                        "caption": "Reels & short-form storytelling",
                    },
                    {
                        "url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
                        "alt": "Product showcase",
                        "caption": "Product unboxing & review",
                    },
                    {
                        "url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=900&q=80",
                        "alt": "Brand collaboration",
                        "caption": "On-site brand activation",
                    },
                    {
                        "url": "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?auto=format&fit=crop&w=900&q=80",
                        "alt": "Lifestyle shoot",
                        "caption": "Lifestyle & travel content",
                    },
                ],
            },
        },
        {
            "id": "qr-demo",
            "type": "qr_codes",
            "active": True,
            "order": 4,
            "data": {
                "items": [
                    {
                        "label": "Zalo QR",
                        "image_url": "https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=zalo://creator-demo",
                        "target_url": "https://zalo.me/creator-demo",
                    },
                    {
                        "label": "Booking QR",
                        "image_url": "https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=https://slost.app/kol/creator-demo",
                        "target_url": "https://slost.app/kol/creator-demo",
                    },
                ]
            },
        },
        {
            "id": "contact-demo",
            "type": "contact",
            "active": True,
            "order": 5,
            "data": {"phone": "0901000001", "zalo": "creator-demo", "messenger": "creator.demo"},
        },
        {
            "id": "booking",
            "type": "booking",
            "active": True,
            "order": 6,
            "data": {
                "title": "Đặt lịch hợp tác",
                "subtitle": "Gửi brief, ngân sách dự kiến và timeline để mình phản hồi trong 24h.",
            },
        },
    ],
}


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            UPDATE user_profiles
            SET
                bio = :bio,
                avatar_url = :avatar_url,
                text_color = :text_color,
                primary_color = :primary_color,
                bg_type = 'gradient',
                bg_value = :bg_value,
                phone = :phone,
                zalo = :zalo,
                messenger = :messenger,
                layout_structure = CAST(:layout AS JSONB)
            WHERE user_id = CAST(:user_id AS UUID)
            """
        ),
        {
            "user_id": KOL_USER_ID,
            "bio": "KOL lifestyle & tech | Sẵn sàng hợp tác thương hiệu FMCG, beauty, fintech.",
            "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=600&q=80",
            "text_color": "#0F172A",
            "primary_color": "#DB2777",
            "bg_value": "linear-gradient(135deg, #FDF2F8 0%, #E0F2FE 100%)",
            "phone": "0901000001",
            "zalo": "creator-demo",
            "messenger": "creator.demo",
            "layout": json.dumps(CREATOR_DEMO_LAYOUT),
        },
    )


def downgrade() -> None:
    pass
