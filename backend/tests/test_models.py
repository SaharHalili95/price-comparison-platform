import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas.product import PriceInfo, ProductWithPrices, SearchResponse, SourceEnum


class TestSourceEnum:
    """Tests for SourceEnum."""

    def test_source_enum_values(self):
        """Test that all source values exist."""
        assert SourceEnum.KSP == "KSP"
        assert SourceEnum.BUG == "Bug"
        assert SourceEnum.ZAP == "Zap"


class TestPriceInfoModel:
    """Tests for PriceInfo schema."""

    def test_create_price_info(self):
        """Test creating a price info object."""
        price = PriceInfo(
            source=SourceEnum.KSP,
            price=99.99,
            url="https://ksp.co.il/web/item/12345"
        )
        assert price.source == SourceEnum.KSP
        assert price.price == 99.99
        assert price.url == "https://ksp.co.il/web/item/12345"
        assert price.availability is True  # default

    def test_price_info_with_all_fields(self):
        """Test price info with all fields."""
        price = PriceInfo(
            source=SourceEnum.BUG,
            price=50.0,
            currency="₪",
            availability=False,
            url="https://www.bug.co.il/item/12345"
        )
        assert price.source == SourceEnum.BUG
        assert price.price == 50.0
        assert price.currency == "₪"
        assert price.availability is False

    def test_price_must_be_positive(self):
        """Test that price must be positive."""
        with pytest.raises(ValueError):
            PriceInfo(source=SourceEnum.KSP, price=-10.0)

    def test_price_rounds_to_two_decimals(self):
        """Test that price is rounded to two decimals."""
        price = PriceInfo(source=SourceEnum.KSP, price=99.999)
        assert price.price == 100.0


class TestProductWithPricesModel:
    """Tests for ProductWithPrices schema."""

    def test_create_product_with_prices(self):
        """Test creating a product with prices."""
        now = datetime.now()
        prices = [
            PriceInfo(source=SourceEnum.KSP, price=100.0),
            PriceInfo(source=SourceEnum.BUG, price=90.0),
        ]

        product = ProductWithPrices(
            id=1,
            name="Samsung Galaxy S24 Ultra",
            description="סמארטפון דגל",
            category="אלקטרוניקה",
            created_at=now,
            updated_at=now,
            prices=prices,
            lowest_price=90.0,
            highest_price=100.0,
            average_price=95.0
        )

        assert product.id == 1
        assert product.name == "Samsung Galaxy S24 Ultra"
        assert len(product.prices) == 2
        assert product.lowest_price == 90.0
        assert product.highest_price == 100.0
        assert product.average_price == 95.0

    def test_product_price_statistics(self):
        """Test product price statistics are calculated correctly."""
        now = datetime.now()
        prices = [
            PriceInfo(source=SourceEnum.KSP, price=100.0),
            PriceInfo(source=SourceEnum.BUG, price=200.0),
            PriceInfo(source=SourceEnum.ZAP, price=150.0),
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

    def test_product_with_empty_prices(self):
        """Test creating a product with empty prices list."""
        now = datetime.now()
        product = ProductWithPrices(
            id=1,
            name="Test Product",
            created_at=now,
            prices=[]
        )

        assert product.prices == []
        assert product.lowest_price is None
        assert product.highest_price is None


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
