import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint returns healthy status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "api" in data
        assert "version" in data
        assert data["docs"] == "/docs"

    def test_health_check_endpoint(self, client):
        """Test detailed health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data


class TestProductSearchEndpoint:
    """Tests for product search endpoint."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_search_products_with_query(self, client):
        """Test searching products with a query."""
        response = client.get("/api/products/search?query=Samsung")
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "Samsung"
        assert "total_results" in data
        assert "products" in data
        assert isinstance(data["products"], list)
        assert data["total_results"] > 0

    def test_search_products_empty_query(self, client):
        """Test that empty query returns validation error."""
        response = client.get("/api/products/search?query=")
        assert response.status_code == 422  # Validation error

    def test_search_products_with_category(self, client):
        """Test searching products with category filter."""
        response = client.get("/api/products/search?query=Samsung&category=אלקטרוניקה")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data

    def test_search_products_response_structure(self, client):
        """Test that search response has correct structure."""
        response = client.get("/api/products/search?query=iPhone")
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "query" in data
        assert "total_results" in data
        assert "products" in data

        # Products should exist and have correct structure
        assert len(data["products"]) > 0
        product = data["products"][0]
        assert "id" in product
        assert "name" in product
        assert "prices" in product

    def test_search_hebrew_query(self, client):
        """Test searching with Hebrew query."""
        response = client.get("/api/products/search?query=אלקטרוניקה")
        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] > 0


class TestCategoriesEndpoint:
    """Tests for categories endpoint."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_list_categories(self, client):
        """Test listing all categories."""
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "stats" in data
        assert "total_categories" in data
        assert isinstance(data["categories"], list)
        assert data["total_categories"] == 8

    def test_get_category_products(self, client):
        """Test getting products by category."""
        # First get available categories
        categories_response = client.get("/api/categories")
        categories = categories_response.json().get("categories", [])

        if categories:
            # Test with first available category
            category = categories[0]
            response = client.get(f"/api/categories/{category}/products")
            assert response.status_code == 200
            data = response.json()
            assert "products" in data


class TestProductsEndpoint:
    """Tests for products listing endpoint."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_list_products_limit_validation_too_high(self, client):
        """Test that limit has valid bounds - too high."""
        response = client.get("/api/products?limit=200")
        assert response.status_code == 422

    def test_list_products_limit_validation_negative(self, client):
        """Test that limit has valid bounds - negative."""
        response = client.get("/api/products?limit=-1")
        assert response.status_code == 422


class TestScraperEndpoints:
    """Tests for scraper status endpoints."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_scraper_status(self, client):
        """Test scraper status endpoint."""
        response = client.get("/api/scraper/status")
        assert response.status_code == 200
        data = response.json()
        assert "scrapers_available" in data
        assert "use_real_scrapers" in data
        assert "message" in data
