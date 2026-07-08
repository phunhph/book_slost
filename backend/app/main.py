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


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
