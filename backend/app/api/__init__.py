from fastapi import APIRouter

from app.api.account_routes import router as account_router
from app.api.auth_routes import router as auth_router
from app.api.health_routes import router as health_router
from app.api.routes import router as prices_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(prices_router)
api_router.include_router(account_router)
