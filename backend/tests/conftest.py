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

from app.main import app


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
