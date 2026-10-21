from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import engine, init_db
from app.core.rate_limiter import limiter
from app.core.middleware import SecurityHeadersMiddleware
from app.api.routes import router
from app.api.auth_routes import router as auth_router
import app.models  # noqa: F401 - ensure all models are imported for table creation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    init_db()
    logger.info(f"🚀 {settings.API_TITLE} v{settings.API_VERSION} started!")
    logger.info("API Documentation available at /docs")
    yield
    # Shutdown
    logger.info("Application shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="""
    Grocery price comparison on Israel's official price-transparency data.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check that actually queries the database."""
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


# Include API routes
app.include_router(auth_router)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
