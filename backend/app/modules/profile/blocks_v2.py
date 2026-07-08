from __future__ import annotations

import uuid
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

BlockType = Literal["hero", "social_links", "gallery", "qr_codes", "about", "booking", "contact"]

ALLOWED_SOCIAL_PLATFORMS = {
    "instagram",
    "tiktok",
    "facebook",
    "youtube",
    "twitter",
    "website",
    "shopee",
    "zalo",
    "other",
}


class ProfileBlock(BaseModel):
    id: str
    type: BlockType
    active: bool = True
    order: int = 0
    data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        allowed = {"hero", "social_links", "gallery", "qr_codes", "about", "booking", "contact"}
        if value not in allowed:
            raise ValueError(f"Unsupported block type: {value}")
        return value


class ProfileLayoutV2(BaseModel):
    version: Literal[2] = 2
    blocks: list[ProfileBlock]


def _new_id() -> str:
    return str(uuid.uuid4())


def _default_data(block_type: BlockType) -> dict[str, Any]:
    if block_type == "social_links":
        return {"items": []}
    if block_type == "gallery":
        return {"layout": "grid", "items": []}
    if block_type == "qr_codes":
        return {"items": []}
    if block_type == "about":
        return {"content": ""}
    if block_type == "contact":
        return {"phone": None, "zalo": None, "messenger": None}
    if block_type == "booking":
        return {"title": "Dat lich choi cung", "subtitle": "Chon goi theo tran hoac theo gio, sau do nhan ma QR thanh toan."}
    return {}


def default_layout_v2(
    *,
    bio: str | None = None,
    phone: str | None = None,
    zalo: str | None = None,
    messenger: str | None = None,
    booking_active: bool = True,
) -> dict[str, Any]:
    blocks: list[ProfileBlock] = []
    order = 0

    blocks.append(ProfileBlock(id="hero", type="hero", active=True, order=order, data={}))
    order += 1

    if bio and bio.strip():
        blocks.append(
            ProfileBlock(
                id=_new_id(),
                type="about",
                active=True,
                order=order,
                data={"content": bio.strip()},
            )
        )
        order += 1

    if phone or zalo or messenger:
        blocks.append(
            ProfileBlock(
                id=_new_id(),
                type="contact",
                active=True,
                order=order,
                data={"phone": phone, "zalo": zalo, "messenger": messenger},
            )
        )
        order += 1

    blocks.append(
        ProfileBlock(
            id="booking",
            type="booking",
            active=booking_active,
            order=order,
            data=_default_data("booking"),
        )
    )
    order += 1

    for block_type in ("social_links", "gallery", "qr_codes"):
        blocks.append(
            ProfileBlock(
                id=_new_id(),
                type=block_type,
                active=False,
                order=order,
                data=_default_data(block_type),
            )
        )
        order += 1

    return ProfileLayoutV2(blocks=blocks).model_dump()


def migrate_layout_to_v2(
    raw: Any,
    *,
    bio: str | None = None,
    phone: str | None = None,
    zalo: str | None = None,
    messenger: str | None = None,
) -> dict[str, Any]:
    if isinstance(raw, dict) and raw.get("version") == 2 and isinstance(raw.get("blocks"), list):
        return normalize_layout_v2(raw)

    v1_blocks = raw if isinstance(raw, list) else []
    v1_map = {block.get("id"): block.get("active", False) for block in v1_blocks if isinstance(block, dict)}

    booking_active = v1_map.get("booking_block", True)
    about_active = v1_map.get("media_block", True)

    layout = default_layout_v2(
        bio=bio if about_active else None,
        phone=phone,
        zalo=zalo,
        messenger=messenger,
        booking_active=booking_active,
    )

    return layout


def normalize_layout_v2(raw: dict[str, Any]) -> dict[str, Any]:
    layout = ProfileLayoutV2.model_validate(raw)
    sorted_blocks = sorted(layout.blocks, key=lambda block: block.order)

    seen_ids: set[str] = set()
    normalized: list[ProfileBlock] = []
    for index, block in enumerate(sorted_blocks):
        block_id = block.id if block.id and block.id not in seen_ids else _new_id()
        seen_ids.add(block_id)
        normalized.append(
            ProfileBlock(
                id=block_id,
                type=block.type,
                active=block.active,
                order=index,
                data=block.data or _default_data(block.type),
            )
        )

    if not any(block.type == "hero" for block in normalized):
        normalized.insert(0, ProfileBlock(id="hero", type="hero", active=True, order=0, data={}))

    if not any(block.type == "booking" for block in normalized):
        normalized.append(
            ProfileBlock(
                id="booking",
                type="booking",
                active=True,
                order=len(normalized),
                data=_default_data("booking"),
            )
        )

    for index, block in enumerate(sorted(normalized, key=lambda item: item.order)):
        block.order = index

    return ProfileLayoutV2(blocks=normalized).model_dump()


def validate_layout_payload(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict) and raw.get("version") == 2:
        return normalize_layout_v2(raw)
    if isinstance(raw, list):
        return migrate_layout_to_v2(raw)
    raise ValueError("layout_structure must be version 2.")
