"""
Base Scraper Class
All specific scrapers inherit from this class
"""

import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class BaseScraper(ABC):
    """
    Base class for all price scrapers.
    Provides common functionality like HTTP requests, parsing, rate limiting, etc.
    """

    def __init__(self, site_name: str, base_url: str):
        """
        Initialize the base scraper.

        Args:
            site_name: Name of the website (e.g., "Zap", "KSP")
            base_url: Base URL of the website
        """
        self.site_name = site_name
        self.base_url = base_url
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def get_page(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Fetch a page and return BeautifulSoup object.

        Args:
            url: URL to fetch
            max_retries: Maximum number of retry attempts

        Returns:
            BeautifulSoup object or None if failed
        """
        for attempt in range(max_retries):
            try:
                # Random delay to avoid detection (1-3 seconds)
                time.sleep(random.uniform(1, 3))

                response = self.session.get(url, timeout=15)
                response.raise_for_status()

                return BeautifulSoup(response.content, 'lxml')

            except requests.RequestException as e:
                print(f"[{self.site_name}] Error fetching {url} (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff

        return None

    def extract_price(self, price_text: str) -> Optional[float]:
        """
        Extract numeric price from text string.

        Args:
            price_text: Price string (e.g., "₪1,299.99" or "1299")

        Returns:
            Float price or None if extraction failed
        """
        if not price_text:
            return None

        try:
            # Remove currency symbols and commas
            price_text = price_text.replace('₪', '').replace('$', '').replace(',', '').strip()
            # Extract numbers and decimal point
            price = float(''.join(c for c in price_text if c.isdigit() or c == '.'))
            return round(price, 2)
        except (ValueError, AttributeError):
            return None

    @abstractmethod
    def search_product(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for products on the website.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of product dictionaries
        """
        pass

    @abstractmethod
    def get_product_details(self, product_url: str) -> Optional[Dict]:
        """
        Get detailed information about a specific product.

        Args:
            product_url: URL of the product page

        Returns:
            Product details dictionary or None
        """
        pass

    def format_product_data(self, raw_data: Dict) -> Dict:
        """
        Format raw scraped data into a standard structure.

        Args:
            raw_data: Raw scraped data

        Returns:
            Formatted product data
        """
        return {
            'source': self.site_name,
            'name': raw_data.get('name', ''),
            'price': raw_data.get('price'),
            'currency': 'ILS',  # Israeli Shekel
            'url': raw_data.get('url', ''),
            'image_url': raw_data.get('image_url'),
            'description': raw_data.get('description'),
            'availability': raw_data.get('availability', True),
            'last_updated': datetime.now(),
            'raw_data': raw_data  # Keep original data for debugging
        }

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
