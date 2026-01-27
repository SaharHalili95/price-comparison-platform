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
        "name": "Test Mouse",
        "description": "A test mouse for testing",
        "category": "Electronics",
        "image_url": "https://example.com/mouse.jpg",
        "base_price": 100.0
    }


@pytest.fixture
def sample_products():
    """Multiple sample products for testing."""
    return [
        {
            "id": 1,
            "name": "Gaming Mouse",
            "description": "High-performance gaming mouse",
            "category": "Electronics",
            "image_url": "https://example.com/mouse1.jpg",
            "base_price": 150.0
        },
        {
            "id": 2,
            "name": "Wireless Keyboard",
            "description": "Bluetooth keyboard",
            "category": "Electronics",
            "image_url": "https://example.com/keyboard.jpg",
            "base_price": 200.0
        },
        {
            "id": 3,
            "name": "USB Hub",
            "description": "4-port USB hub",
            "category": "Accessories",
            "image_url": "https://example.com/hub.jpg",
            "base_price": 50.0
        }
    ]
