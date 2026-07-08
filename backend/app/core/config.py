from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Affiliate Booking Core API"
    app_env: str = "development"
    app_debug: bool = True
    api_prefix: str = "/api"

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "affiliate_booking_core"

    cors_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:3001,http://127.0.0.1:3001,"
        "http://localhost:3002,http://127.0.0.1:3002"
    )
    # Allow Vite "Network" URLs (e.g. http://192.168.x.x:3002) during local dev.
    cors_origin_regex: str = (
        r"https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d+)?"
    )

    jwt_secret_key: str = "change-me-in-production-use-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/callback"

    admin_frontend_url: str = "http://localhost:3000"
    client_frontend_url: str = "http://localhost:3001"
    kol_frontend_url: str = "http://localhost:3002"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            "postgresql+psycopg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def frontend_callback_url(self, app_target: str) -> str:
        if app_target == "client":
            base = self.client_frontend_url
        elif app_target == "kol":
            base = self.kol_frontend_url
        else:
            base = self.admin_frontend_url
        return f"{base.rstrip('/')}/auth/google/callback"


@lru_cache
def get_settings() -> Settings:
    return Settings()
