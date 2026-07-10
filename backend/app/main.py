from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.uploads import uploads_root
from app.modules.auth.oauth_routers import router as oauth_router
from app.modules.auth.routers import router as auth_router
from app.modules.booking.routers import (
    admin_router,
    customer_router,
    kol_router,
    router as booking_router,
)
from app.modules.profile.routers import router as profile_router


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploads_path = uploads_root()
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

app.include_router(oauth_router)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(booking_router, prefix=settings.api_prefix)
app.include_router(admin_router, prefix=settings.api_prefix)
app.include_router(customer_router, prefix=settings.api_prefix)
app.include_router(kol_router, prefix=settings.api_prefix)
app.include_router(profile_router, prefix=settings.api_prefix)


@app.on_event("startup")
def seed_default_platforms():
    from app.core.database import SessionLocal
    from app.modules.profile.models import SocialPlatform
    from sqlalchemy import select

    db = SessionLocal()
    try:
        stmt = select(SocialPlatform)
        exists = db.scalars(stmt).first()
        if not exists:
            defaults = [
                {"key": "phone", "label": "Điện thoại", "category": "contact"},
                {"key": "zalo", "label": "Zalo", "category": "contact"},
                {"key": "messenger", "label": "Facebook Messenger", "category": "contact"},
                {"key": "telegram", "label": "Telegram", "category": "contact"},
                {"key": "viber", "label": "Viber", "category": "contact"},
                {"key": "instagram", "label": "Instagram", "category": "social"},
                {"key": "tiktok", "label": "TikTok", "category": "social"},
                {"key": "facebook", "label": "Facebook", "category": "social"},
                {"key": "youtube", "label": "YouTube", "category": "social"},
                {"key": "twitter", "label": "X / Twitter", "category": "social"},
                {"key": "shopee", "label": "Shopee", "category": "social"},
                {"key": "playduo", "label": "Playduo", "category": "social"},
                {"key": "playdual", "label": "Playdual", "category": "social"},
                {"key": "zpay", "label": "Zpay", "category": "social"},
                {"key": "website", "label": "Website", "category": "social"},
                {"key": "other", "label": "Liên kết khác", "category": "social"},
            ]
            for item in defaults:
                db.add(SocialPlatform(**item))
            db.commit()
    except Exception as exc:
        print(f"Error seeding platforms: {exc}")
    finally:
        db.close()


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
