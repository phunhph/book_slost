from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

MAX_PROOF_BYTES = 5 * 1024 * 1024


def uploads_root() -> Path:
    root = Path(__file__).resolve().parents[2] / "uploads"
    root.mkdir(parents=True, exist_ok=True)
    return root


def payment_proofs_dir() -> Path:
    path = uploads_root() / "payment_proofs"
    path.mkdir(parents=True, exist_ok=True)
    return path


async def save_payment_proof(file: UploadFile) -> str:
    content_type = (file.content_type or "").lower().strip()
    extension = ALLOWED_CONTENT_TYPES.get(content_type)
    if not extension:
        raise ValueError("Chỉ chấp nhận ảnh bill định dạng JPG, PNG, WEBP hoặc GIF.")

    data = await file.read()
    if not data:
        raise ValueError("File bill trống.")
    if len(data) > MAX_PROOF_BYTES:
        raise ValueError("File bill tối đa 5MB.")

    filename = f"{uuid.uuid4().hex}{extension}"
    target = payment_proofs_dir() / filename
    target.write_bytes(data)
    return f"/uploads/payment_proofs/{filename}"
