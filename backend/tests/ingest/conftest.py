import pytest
from sqlalchemy import text

from app.core.database import SessionLocal


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
