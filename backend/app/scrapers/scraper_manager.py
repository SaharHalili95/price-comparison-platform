"""
Scraper Manager
Coordinates multiple scrapers and aggregates results
"""

from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from .zap_scraper import ZapScraper
from .ksp_scraper import KSPScraper
from .bug_scraper import BugScraper


class ScraperManager:
    """
    Manages multiple scrapers and aggregates their results.
    Provides parallel scraping capabilities for faster results.
    """

    def __init__(self, enabled_scrapers: Optional[List[str]] = None):
        """
        Initialize the scraper manager.

        Args:
            enabled_scrapers: List of scraper names to enable.
                            If None, all scrapers are enabled.
                            Options: ['zap', 'ksp', 'bug']
        """
        self.scrapers = {}

        # Initialize scrapers based on enabled list
        if enabled_scrapers is None or 'zap' in enabled_scrapers:
            self.scrapers['zap'] = ZapScraper()

        if enabled_scrapers is None or 'ksp' in enabled_scrapers:
            self.scrapers['ksp'] = KSPScraper()

        if enabled_scrapers is None or 'bug' in enabled_scrapers:
            self.scrapers['bug'] = BugScraper()

        print(f"[ScraperManager] Initialized with scrapers: {list(self.scrapers.keys())}")

    def search_all_parallel(self, query: str, max_results_per_site: int = 10) -> Dict[str, List[Dict]]:
        """
        Search all enabled scrapers in parallel for faster results.

        Args:
            query: Search query
            max_results_per_site: Maximum results per scraper

        Returns:
            Dictionary with scraper names as keys and results as values
        """
        print(f"[ScraperManager] Starting parallel search for: {query}")
        results = {}

        with ThreadPoolExecutor(max_workers=len(self.scrapers)) as executor:
            # Submit all scraping tasks
            future_to_scraper = {
                executor.submit(scraper.search_product, query, max_results_per_site): name
                for name, scraper in self.scrapers.items()
            }

            # Collect results as they complete
            for future in as_completed(future_to_scraper):
                scraper_name = future_to_scraper[future]
                try:
                    scraper_results = future.result(timeout=30)  # 30 second timeout
                    results[scraper_name] = scraper_results
                    print(f"[ScraperManager] {scraper_name} returned {len(scraper_results)} results")
                except Exception as e:
                    print(f"[ScraperManager] Error with {scraper_name}: {e}")
                    results[scraper_name] = []

        return results

    def search_all_sequential(self, query: str, max_results_per_site: int = 10) -> Dict[str, List[Dict]]:
        """
        Search all enabled scrapers sequentially (slower but more reliable).

        Args:
            query: Search query
            max_results_per_site: Maximum results per scraper

        Returns:
            Dictionary with scraper names as keys and results as values
        """
        print(f"[ScraperManager] Starting sequential search for: {query}")
        results = {}

        for name, scraper in self.scrapers.items():
            try:
                scraper_results = scraper.search_product(query, max_results_per_site)
                results[name] = scraper_results
                print(f"[ScraperManager] {name} returned {len(scraper_results)} results")
            except Exception as e:
                print(f"[ScraperManager] Error with {name}: {e}")
                results[name] = []

        return results

    def aggregate_results(self, scraper_results: Dict[str, List[Dict]]) -> List[Dict]:
        """
        Aggregate and deduplicate results from multiple scrapers.

        Args:
            scraper_results: Dictionary of results from each scraper

        Returns:
            Aggregated list of products with price comparisons
        """
        # Dictionary to group products by similar names
        product_map = {}

        for scraper_name, products in scraper_results.items():
            for product in products:
                # Normalize product name for matching
                normalized_name = self._normalize_product_name(product.get('name', ''))

                if not normalized_name:
                    continue

                # If this product exists, add pricing info
                if normalized_name in product_map:
                    existing = product_map[normalized_name]

                    # Add this source's price to the list
                    if 'prices' not in existing:
                        existing['prices'] = []

                    existing['prices'].append({
                        'source': product['source'],
                        'price': product.get('price'),
                        'currency': product.get('currency', 'ILS'),
                        'url': product.get('url'),
                        'availability': product.get('availability', True),
                        'last_updated': product.get('last_updated')
                    })

                    # Update price statistics
                    self._update_price_statistics(existing)

                else:
                    # New product - initialize it
                    product_map[normalized_name] = {
                        'name': product.get('name'),
                        'description': product.get('description'),
                        'image_url': product.get('image_url'),
                        'category': product.get('category'),
                        'prices': [{
                            'source': product['source'],
                            'price': product.get('price'),
                            'currency': product.get('currency', 'ILS'),
                            'url': product.get('url'),
                            'availability': product.get('availability', True),
                            'last_updated': product.get('last_updated')
                        }]
                    }
                    self._update_price_statistics(product_map[normalized_name])

        # Convert to list and sort by number of available prices
        aggregated = list(product_map.values())
        aggregated.sort(key=lambda x: len(x.get('prices', [])), reverse=True)

        print(f"[ScraperManager] Aggregated {len(aggregated)} unique products")
        return aggregated

    def _normalize_product_name(self, name: str) -> str:
        """
        Normalize product name for better matching across sites.

        Args:
            name: Raw product name

        Returns:
            Normalized product name
        """
        if not name:
            return ''

        # Convert to lowercase and remove extra spaces
        normalized = ' '.join(name.lower().split())

        # Remove common words that don't help matching
        remove_words = ['מקורי', 'חדש', 'new', 'original', 'משלוח חינם', 'free shipping']
        for word in remove_words:
            normalized = normalized.replace(word, '')

        # Clean up
        normalized = ' '.join(normalized.split())

        return normalized

    def _update_price_statistics(self, product: Dict) -> None:
        """
        Calculate and update price statistics for a product.

        Args:
            product: Product dictionary (modified in place)
        """
        prices = [p['price'] for p in product.get('prices', [])
                  if p.get('price') and p.get('availability')]

        if not prices:
            product['lowest_price'] = None
            product['highest_price'] = None
            product['average_price'] = None
            return

        product['lowest_price'] = round(min(prices), 2)
        product['highest_price'] = round(max(prices), 2)
        product['average_price'] = round(sum(prices) / len(prices), 2)

        # Calculate savings
        if product['lowest_price'] and product['highest_price']:
            savings = product['highest_price'] - product['lowest_price']
            savings_percent = (savings / product['highest_price']) * 100
            product['potential_savings'] = round(savings, 2)
            product['savings_percent'] = round(savings_percent, 1)

    def get_product_comparison(self, product_name: str) -> Optional[Dict]:
        """
        Get detailed price comparison for a specific product.

        Args:
            product_name: Name of the product

        Returns:
            Product comparison data or None
        """
        results = self.search_all_parallel(product_name, max_results_per_site=5)
        aggregated = self.aggregate_results(results)

        if not aggregated:
            return None

        # Return the best match (first result after aggregation)
        return aggregated[0]

    def close_all(self):
        """Close all scraper sessions"""
        for scraper in self.scrapers.values():
            scraper.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_all()
