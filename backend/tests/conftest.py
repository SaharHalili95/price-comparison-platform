import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# app.core.config.Settings() rejects the default placeholder JWT secret
# outside DEBUG mode (see config.py). Tests don't need a real secret, but
# importing app.main below instantiates Settings() immediately - without
# this, anyone running `pytest` locally with a clean shell hits a crash at
# collection time instead of getting test results.
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-not-for-production-use-1234567890")


def _use_fresh_test_database() -> None:
    """Point the app at <db>_test and recreate it empty, so tests never touch development data."""
    import psycopg
    from sqlalchemy.engine import make_url

    url = make_url(os.environ.get("DATABASE_URL", "postgresql+psycopg://salsmart:salsmart@localhost:5432/salsmart"))
    test_url = url.set(database=f"{url.database}_test")
    admin = url.set(drivername="postgresql", database="postgres").render_as_string(hide_password=False)
    with psycopg.connect(admin, autocommit=True) as connection:
        connection.execute(f'DROP DATABASE IF EXISTS "{test_url.database}" WITH (FORCE)')
        connection.execute(f'CREATE DATABASE "{test_url.database}"')
    os.environ["DATABASE_URL"] = test_url.render_as_string(hide_password=False)


_use_fresh_test_database()

from app.core.database import init_db  # noqa: E402
from app.main import app  # noqa: E402

init_db()


@pytest.fixture
def client():
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def admin_token(client):
    """
    A valid JWT for an admin user, for endpoints behind require_admin
    (e.g. /api/scraper/status, /api/scraper/test).

    Gets-or-creates a fixed admin row rather than inserting a fresh one
    per run, since tests share the database configured by
    DATABASE_URL and a duplicate insert would hit the unique constraint
    on a second test run.
    """
    from app.core.database import SessionLocal
    from app.core.security import create_access_token, hash_password
    from app.models.user import User

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "test-admin").first()
        if user is None:
            user = User(
                email="test-admin@example.com",
                username="test-admin",
                hashed_password=hash_password("not-a-real-password"),
                role="admin",
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        token, _jti, _expires = create_access_token(subject=user.id, role="admin")
        return token
    finally:
        db.close()


from sqlalchemy import text  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402


@pytest.fixture
def session():
    db = SessionLocal()
    db.execute(text("TRUNCATE price_history, current_prices, items, stores, ingestion_runs, chains RESTART IDENTITY CASCADE"))
    db.commit()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Sign-in endpoints allow 10 requests a minute; tests sign in far more often than that."""
    from app.core.rate_limiter import limiter

    limiter.reset()
    yield
