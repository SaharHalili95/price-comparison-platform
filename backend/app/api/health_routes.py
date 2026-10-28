import logging

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import engine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/")
async def root():
    return {
        "status": "healthy",
        "api": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": "/docs"
    }


@router.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        database = "ok"
    except SQLAlchemyError:
        logger.exception("Database health check failed")
        database = "error"
    return {
        "status": "healthy" if database == "ok" else "degraded",
        "api": settings.API_TITLE,
        "version": settings.API_VERSION,
        "database": database,
    }
