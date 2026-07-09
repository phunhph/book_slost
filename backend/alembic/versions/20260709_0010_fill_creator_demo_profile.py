"""fill creator demo profile with complete showcase data

Revision ID: 20260709_0010
Revises: 20260708_0009
Create Date: 2026-07-09 14:28:00
"""

from __future__ import annotations

import json

from alembic import op
import sqlalchemy as sa


revision = "20260709_0010"
down_revision = "20260708_0009"
branch_labels = None
depends_on = None


CREATOR_LAYOUT = {
    "version": 2,
    "blocks": [
        {"id": "hero", "type": "hero", "active": True, "order": 0, "data": {}},
        {
            "id": "social-demo",
            "type": "social_links",
            "active": True,
            "order": 1,
            "data": {
                "items": [
                    {"platform": "facebook", "label": "Facebook", "url": "https://facebook.com/creator.demo"},
                    {"platform": "instagram", "label": "Instagram", "url": "https://instagram.com/creator.demo"},
                    {"platform": "tiktok", "label": "TikTok", "url": "https://tiktok.com/@creatordemo"},
                    {"platform": "youtube", "label": "YouTube", "url": "https://youtube.com/@creatordemo"},
                    {"platform": "website", "label": "Website", "url": "https://slost.app/kol/creator-demo"},
                ]
            },
        },
        {
            "id": "contact-demo",
            "type": "contact",
            "active": True,
            "order": 2,
            "data": {"phone": "0901000001", "zalo": "creator-demo", "messenger": "creator.demo"},
        },
        {
            "id": "about-demo",
            "type": "about",
            "active": True,
            "order": 3,
            "data": {
                "content": (
                    "<p><strong>Creator Demo</strong> là KOL lifestyle & tech, tập trung review sản phẩm, short-form video "
                    "và storytelling cho chiến dịch thương hiệu.</p>"
                    "<ul>"
                    "<li>120K+ followers trên TikTok, Instagram và Facebook</li>"
                    "<li>Engagement trung bình 6.8%</li>"
                    "<li>Đã hợp tác với 30+ brand thuộc FMCG, beauty, fintech</li>"
                    "</ul>"
                    "<p>Nhận booking review, livestream, UGC, launch sản phẩm và campaign dài hạn.</p>"
                )
            },
        },
        {
            "id": "gallery-demo",
            "type": "gallery",
            "active": True,
            "order": 4,
            "data": {
                "layout": "grid",
                "items": [
                    {
                        "url": "https://images.unsplash.com/photo-1611162617474-5b21e039e566?auto=format&fit=crop&w=900&q=80",
                        "alt": "TikTok studio setup",
                        "caption": "Short-form video production",
                    },
                    {
                        "url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80",
                        "alt": "Product unboxing",
                        "caption": "Product unboxing & review",
                    },
                    {
                        "url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=900&q=80",
                        "alt": "Brand activation event",
                        "caption": "On-site brand activation",
                    },
                    {
                        "url": "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?auto=format&fit=crop&w=900&q=80",
                        "alt": "Lifestyle creator shoot",
                        "caption": "Lifestyle & travel content",
                    },
                ],
            },
        },
        {
            "id": "qr-demo",
            "type": "qr_codes",
            "active": True,
            "order": 5,
            "data": {
                "items": [
                    {
                        "label": "Zalo QR",
                        "image_url": "https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=zalo://creator-demo",
                        "target_url": "https://zalo.me/creator-demo",
                    },
                    {
                        "label": "Trang booking",
                        "image_url": "https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=https://slost.app/kol/creator-demo",
                        "target_url": "https://slost.app/kol/creator-demo",
                    },
                ]
            },
        },
        {
            "id": "booking",
            "type": "booking",
            "active": True,
            "order": 6,
            "data": {
                "title": "Đặt lịch hợp tác",
                "subtitle": "Gửi brief, KPI, ngân sách và timeline để mình phản hồi trong 24h.",
            },
        },
    ],
}


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            UPDATE user_profiles AS p
            SET
                display_name = 'Creator Demo',
                username = 'creator-demo',
                bio = :bio,
                avatar_url = :avatar_url,
                theme_mode = 'custom',
                font_family = 'Be Vietnam Pro',
                primary_color = '#DB2777',
                text_color = '#0F172A',
                bg_type = 'gradient',
                bg_value = 'linear-gradient(135deg, #FDF2F8 0%, #E0F2FE 100%)',
                avatar_style = 'rounded',
                button_style = 'shadow',
                phone = '0901000001',
                zalo = 'creator-demo',
                messenger = 'creator.demo',
                pricing_type = 'match',
                price_per_match = 150000,
                price_per_hour = 100000,
                currency = 'VND',
                layout_structure = CAST(:layout AS JSONB)
            FROM users AS u
            WHERE p.user_id = u.id
              AND u.email = 'creator@example.com'
            """
        ),
        {
            "bio": "KOL lifestyle & tech | Review sản phẩm, UGC, livestream và campaign thương hiệu dài hạn.",
            "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=600&q=80",
            "layout": json.dumps(CREATOR_LAYOUT),
        },
    )


def downgrade() -> None:
    pass
