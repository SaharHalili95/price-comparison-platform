import random
from typing import List
from datetime import datetime
from app.schemas.product import PriceInfo, SourceEnum, ProductWithPrices


class PriceScraper:
    """
    Simulates price scraping from multiple sources.
    In production, this would make actual HTTP requests to different retailers.
    """

    SOURCES = [SourceEnum.AMAZON, SourceEnum.EBAY, SourceEnum.WALMART]

    def __init__(self):
        """Initialize the price scraper"""
        pass

    def scrape_prices(self, product_name: str, base_price: float = None) -> List[PriceInfo]:
        """
        Simulate scraping prices from multiple sources.

        Args:
            product_name: Name of the product to search for
            base_price: Optional base price to generate variations from

        Returns:
            List of PriceInfo objects from different sources
        """
        if base_price is None:
            base_price = random.uniform(20.0, 200.0)

        prices = []

        for source in self.SOURCES:
            # Simulate price variation between sources (±20%)
            variation = random.uniform(-0.20, 0.20)
            price = base_price * (1 + variation)

            # Random availability (90% chance of being available)
            availability = random.random() > 0.1

            price_info = PriceInfo(
                source=source,
                price=round(price, 2),
                currency="USD",
                availability=availability,
                url=self._generate_url(source, product_name),
                last_updated=datetime.now()
            )
            prices.append(price_info)

        return prices

    def _generate_url(self, source: SourceEnum, product_name: str) -> str:
        """Generate a mock URL for the product on the given source"""
        product_slug = product_name.lower().replace(" ", "-")

        url_mapping = {
            SourceEnum.AMAZON: f"https://amazon.com/dp/{product_slug}",
            SourceEnum.EBAY: f"https://ebay.com/itm/{product_slug}",
            SourceEnum.WALMART: f"https://walmart.com/ip/{product_slug}"
        }

        return url_mapping.get(source, "#")

    def get_price_statistics(self, prices: List[PriceInfo]) -> dict:
        """
        Calculate price statistics from the list of prices.

        Args:
            prices: List of PriceInfo objects

        Returns:
            Dictionary with lowest, highest, and average prices
        """
        available_prices = [p.price for p in prices if p.availability]

        if not available_prices:
            return {
                "lowest_price": None,
                "highest_price": None,
                "average_price": None
            }

        return {
            "lowest_price": round(min(available_prices), 2),
            "highest_price": round(max(available_prices), 2),
            "average_price": round(sum(available_prices) / len(available_prices), 2)
        }


# Sample product database - in production this would be in the actual database
SAMPLE_PRODUCTS = [
    {
        "id": 1,
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse with USB receiver",
        "category": "Electronics",
        "image_url": "https://images.unsplash.com/photo-1527814050087-3793815479db?w=400",
        "base_price": 29.99
    },
    {
        "id": 2,
        "name": "Mechanical Keyboard",
        "description": "RGB mechanical keyboard with blue switches",
        "category": "Electronics",
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400",
        "base_price": 89.99
    },
    {
        "id": 3,
        "name": "USB-C Hub",
        "description": "7-in-1 USB-C hub with HDMI and card reader",
        "category": "Electronics",
        "image_url": "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=400",
        "base_price": 45.99
    },
    {
        "id": 4,
        "name": "Webcam HD 1080p",
        "description": "Full HD webcam with built-in microphone",
        "category": "Electronics",
        "image_url": "https://images.unsplash.com/photo-1588508065123-287b28e013da?w=400",
        "base_price": 69.99
    },
    {
        "id": 5,
        "name": "Laptop Stand",
        "description": "Adjustable aluminum laptop stand",
        "category": "Accessories",
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400",
        "base_price": 39.99
    },
    {
        "id": 6,
        "name": "Bluetooth Headphones",
        "description": "Over-ear wireless headphones with noise cancellation",
        "category": "Audio",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
        "base_price": 149.99
    },
    {
        "id": 7,
        "name": "Portable SSD 1TB",
        "description": "Fast external solid-state drive",
        "category": "Storage",
        "image_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=400",
        "base_price": 119.99
    },
    {
        "id": 8,
        "name": "Monitor 27 inch",
        "description": "4K IPS monitor with HDR support",
        "category": "Displays",
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400",
        "base_price": 349.99
    }
]


def get_sample_products():
    """Get sample products for testing"""
    return SAMPLE_PRODUCTS
