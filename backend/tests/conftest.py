import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_product():
    """Sample product data for testing."""
    return {
        "id": 1,
        "name": "iPhone 15 Pro Max 256GB",
        "description": "iPhone 15 Pro Max עם מסך 6.7 אינץ׳",
        "category": "אלקטרוניקה",
        "image_url": None,
        "base_price": 5299.0
    }


@pytest.fixture
def sample_products():
    """Multiple sample products for testing."""
    return [
        {
            "id": 1,
            "name": "iPhone 15 Pro Max 256GB",
            "description": "iPhone 15 Pro Max עם מסך 6.7 אינץ׳",
            "category": "אלקטרוניקה",
            "image_url": None,
            "base_price": 5299.0
        },
        {
            "id": 201,
            "name": "MacBook Air M3 15\" 16GB 512GB",
            "description": "MacBook Air עם שבב M3",
            "category": "מחשבים",
            "image_url": None,
            "base_price": 6299.0
        },
        {
            "id": 401,
            "name": "Nike Air Max 90",
            "description": "נעלי Nike Air Max 90 קלאסיות",
            "category": "אופנה",
            "image_url": None,
            "base_price": 549.0
        }
    ]
