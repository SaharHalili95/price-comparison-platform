import random
from typing import List
from datetime import datetime, timezone
from app.schemas.product import PriceInfo, SourceEnum


class PriceScraper:
    """
    Simulates price scraping from multiple Israeli sources.
    In production, this would make actual HTTP requests to KSP, Bug, and Zap.
    """

    SOURCES = [SourceEnum.KSP, SourceEnum.BUG, SourceEnum.ZAP]

    def scrape_prices(self, product_name: str, base_price: float = None) -> List[PriceInfo]:
        """
        Simulate scraping prices from multiple Israeli sources.

        Args:
            product_name: Name of the product to search for
            base_price: Optional base price to generate variations from

        Returns:
            List of PriceInfo objects from different sources
        """
        if base_price is None:
            base_price = random.uniform(50.0, 2000.0)

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
                currency="₪",
                availability=availability,
                url=self._generate_url(source, product_name),
                last_updated=datetime.now(timezone.utc)
            )
            prices.append(price_info)

        return prices

    def _generate_url(self, source: SourceEnum, product_name: str) -> str:
        """Generate a mock URL for the product on the given Israeli source"""
        product_slug = product_name.lower().replace(" ", "-")

        url_mapping = {
            SourceEnum.KSP: f"https://ksp.co.il/web/search?text={product_slug}",
            SourceEnum.BUG: f"https://www.bug.co.il/search?q={product_slug}",
            SourceEnum.ZAP: f"https://www.zap.co.il/search.aspx?keyword={product_slug}"
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
