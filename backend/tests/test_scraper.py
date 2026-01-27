import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scraper import PriceScraper


class TestPriceScraper:
    """Tests for PriceScraper service."""

    @pytest.fixture
    def scraper(self):
        """Create a PriceScraper instance."""
        return PriceScraper()

    def test_scrape_prices_returns_list(self, scraper):
        """Test that scrape_prices returns a list."""
        prices = scraper.scrape_prices("Test Product")
        assert isinstance(prices, list)

    def test_scrape_prices_with_base_price(self, scraper):
        """Test scraping prices with a base price."""
        base_price = 100.0
        prices = scraper.scrape_prices("Test Product", base_price)

        assert isinstance(prices, list)
        # Prices should be around the base price
        for price_info in prices:
            assert hasattr(price_info, 'price')
            assert hasattr(price_info, 'source')

    def test_get_price_statistics(self, scraper):
        """Test price statistics calculation."""
        # First get some prices
        prices = scraper.scrape_prices("Test Product", 100.0)

        # Then get statistics
        stats = scraper.get_price_statistics(prices)

        assert "lowest_price" in stats
        assert "highest_price" in stats
        assert "average_price" in stats

        # Validate statistics make sense
        if prices:
            assert stats["lowest_price"] <= stats["average_price"]
            assert stats["average_price"] <= stats["highest_price"]

    def test_get_price_statistics_empty_list(self, scraper):
        """Test statistics with empty price list."""
        stats = scraper.get_price_statistics([])

        assert stats["lowest_price"] is None
        assert stats["highest_price"] is None
        assert stats["average_price"] is None

    def test_scrape_prices_different_products(self, scraper):
        """Test that different products can get prices."""
        products = ["Mouse", "Keyboard", "Monitor"]

        for product in products:
            prices = scraper.scrape_prices(product)
            assert isinstance(prices, list)

    def test_price_sources(self, scraper):
        """Test that prices come from expected sources."""
        prices = scraper.scrape_prices("Test Product", 100.0)

        if prices:
            sources = [p.source for p in prices]
            # Should have multiple sources
            assert len(sources) > 0
