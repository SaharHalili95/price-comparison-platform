from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.routes import router

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
    logger.info(f"📚 API Documentation: http://localhost:8000/docs")
    yield
    # Shutdown
    logger.info("Application shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="""
    Smart Price Comparison Platform API

    This API provides endpoints to:
    * Search for products
    * Get product details with price comparisons
    * Compare prices from multiple sources (Amazon, eBay, Walmart)

    All price data is validated using Pydantic models for data integrity.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
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
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "api": settings.API_TITLE,
        "version": settings.API_VERSION,
        "database": "connected"
    }


# Include API routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
