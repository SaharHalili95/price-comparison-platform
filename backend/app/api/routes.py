from fastapi import APIRouter

# Grocery search and comparison routes are added in Phase 2, on top of the ingested price data.
router = APIRouter(prefix="/api", tags=["prices"])
