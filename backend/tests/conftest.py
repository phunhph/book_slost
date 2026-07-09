from __future__ import annotations

import os
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from pathlib import Path
import sys
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Keep settings deterministic for tests before app import.
os.environ.setdefault("JWT_SECRET_KEY", "unit-test-secret-key-not-for-production-32b")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("APP_DEBUG", "false")

from app.core.config import get_settings
from app.core.database import Base, get_db
from app.main import app
from app.modules.auth.models import User
from app.modules.auth.services import hash_password
from app.modules.profile.models import UserProfile


get_settings.cache_clear()


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(_type, _compiler, **_kw):  # noqa: ANN001
    return "JSON"


@compiles(PGUUID, "sqlite")
def _compile_uuid_sqlite(_type, _compiler, **_kw):  # noqa: ANN001
    return "CHAR(36)"


@pytest.fixture()
def db_engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):  # noqa: ANN001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def db_session(db_engine) -> Generator[Session, None, None]:
    TestingSessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False, future=True)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def _override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def seed_users(db_session: Session) -> dict[str, User]:
    admin = User(
        id=uuid4(),
        email="admin@example.com",
        password_hash=hash_password("Admin@123"),
        auth_provider="local",
        role="admin",
        is_active=True,
    )
    kol = User(
        id=uuid4(),
        email="kol@example.com",
        password_hash=hash_password("Creator@123"),
        auth_provider="local",
        role="kol",
        is_active=True,
    )
    kol_no_bank = User(
        id=uuid4(),
        email="kol-nobank@example.com",
        password_hash=hash_password("Creator@123"),
        auth_provider="local",
        role="kol",
        is_active=True,
    )
    customer = User(
        id=uuid4(),
        email="customer@example.com",
        password_hash=hash_password("Customer@123"),
        auth_provider="local",
        role="customer",
        is_active=True,
    )

    db_session.add_all([admin, kol, kol_no_bank, customer])
    db_session.flush()

    db_session.add_all(
        [
            UserProfile(
                user_id=admin.id,
                username="admin-test",
                display_name="Admin Test",
            ),
            UserProfile(
                user_id=kol.id,
                username="kol-test",
                display_name="KOL Test",
                bio="KOL co bang gia va STK",
                primary_color="#8B5CF6",
                pricing_type="match",
                price_per_match=150000,
                price_per_hour=100000,
                currency="VND",
                bank_name="Vietcombank (VCB)",
                bank_code="970436",
                bank_account_number="0123456789",
                bank_account_name="KOL TEST",
                phone="0901000001",
                zalo="kol-test",
            ),
            UserProfile(
                user_id=kol_no_bank.id,
                username="kol-nobank",
                display_name="KOL No Bank",
                pricing_type="match",
                price_per_match=120000,
                price_per_hour=80000,
                currency="VND",
            ),
            UserProfile(
                user_id=customer.id,
                username="customer-test",
                display_name="Customer Test",
                phone="0901000002",
                zalo="customer-test",
            ),
        ]
    )
    db_session.commit()

    return {
        "admin": admin,
        "kol": kol,
        "kol_no_bank": kol_no_bank,
        "customer": customer,
    }


@pytest.fixture()
def future_schedule() -> datetime:
    return datetime.now(UTC) + timedelta(days=2)
