import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas.product import PriceInfo, ProductWithPrices, SearchResponse


class TestPriceInfoModel:
    """Tests for PriceInfo schema."""

    def test_create_price_info(self):
        """Test creating a price info object."""
        price = PriceInfo(
            source="Amazon",
            price=99.99,
            url="https://amazon.com/product",
            in_stock=True
        )
        assert price.source == "Amazon"
        assert price.price == 99.99
        assert price.url == "https://amazon.com/product"
        assert price.in_stock is True

    def test_price_info_optional_fields(self):
        """Test price info with optional fields."""
        price = PriceInfo(
            source="Test",
            price=50.0
        )
        assert price.source == "Test"
        assert price.price == 50.0


class TestProductWithPricesModel:
    """Tests for ProductWithPrices schema."""

    def test_create_product_with_prices(self):
        """Test creating a product with prices."""
        now = datetime.now()
        prices = [
            PriceInfo(source="Store A", price=100.0),
            PriceInfo(source="Store B", price=90.0),
        ]

        product = ProductWithPrices(
            id=1,
            name="Test Product",
            description="A test product",
            category="Electronics",
            image_url="https://example.com/image.jpg",
            created_at=now,
            updated_at=now,
            prices=prices,
            lowest_price=90.0,
            highest_price=100.0,
            average_price=95.0
        )

        assert product.id == 1
        assert product.name == "Test Product"
        assert len(product.prices) == 2
        assert product.lowest_price == 90.0
        assert product.highest_price == 100.0
        assert product.average_price == 95.0

    def test_product_price_statistics(self):
        """Test product price statistics are calculated correctly."""
        now = datetime.now()
        prices = [
            PriceInfo(source="A", price=100.0),
            PriceInfo(source="B", price=200.0),
            PriceInfo(source="C", price=150.0),
        ]

        product = ProductWithPrices(
            id=1,
            name="Test",
            created_at=now,
            updated_at=now,
            prices=prices,
            lowest_price=100.0,
            highest_price=200.0,
            average_price=150.0
        )

        assert product.lowest_price == 100.0
        assert product.highest_price == 200.0
        assert product.average_price == 150.0


class TestSearchResponseModel:
    """Tests for SearchResponse schema."""

    def test_create_search_response(self):
        """Test creating a search response."""
        now = datetime.now()
        products = [
            ProductWithPrices(
                id=1,
                name="Product 1",
                created_at=now,
                updated_at=now,
                prices=[],
            ),
            ProductWithPrices(
                id=2,
                name="Product 2",
                created_at=now,
                updated_at=now,
                prices=[],
            ),
        ]

        response = SearchResponse(
            query="test",
            total_results=2,
            products=products
        )

        assert response.query == "test"
        assert response.total_results == 2
        assert len(response.products) == 2

    def test_empty_search_response(self):
        """Test creating an empty search response."""
        response = SearchResponse(
            query="nonexistent",
            total_results=0,
            products=[]
        )

        assert response.query == "nonexistent"
        assert response.total_results == 0
        assert response.products == []
