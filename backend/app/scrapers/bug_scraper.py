"""
Bug Scraper
Major Israeli electronics retail chain
"""

from typing import List, Dict, Optional
from urllib.parse import quote
from .base_scraper import BaseScraper


class BugScraper(BaseScraper):
    """
    Scraper for Bug.co.il - Major Israeli electronics retailer
    """

    def __init__(self):
        super().__init__(
            site_name="Bug",
            base_url="https://www.bug.co.il"
        )
        self.search_url = f"{self.base_url}/search"

    def search_product(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for products on Bug.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of product dictionaries
        """
        products = []
        encoded_query = quote(query)
        search_url = f"{self.search_url}?q={encoded_query}"

        print(f"[Bug] Searching for: {query}")
        soup = self.get_page(search_url)

        if not soup:
            print(f"[Bug] Failed to fetch search results")
            return products

        try:
            # Bug uses product cards
            product_items = soup.find_all('div', class_='product-card', limit=max_results)

            if not product_items:
                # Try alternative selectors
                product_items = soup.find_all('div', class_='item-product', limit=max_results)
                if not product_items:
                    product_items = soup.find_all('article', class_='product', limit=max_results)

            for item in product_items:
                try:
                    product_data = self._parse_product_item(item)
                    if product_data:
                        products.append(self.format_product_data(product_data))
                except Exception as e:
                    print(f"[Bug] Error parsing product item: {e}")
                    continue

            print(f"[Bug] Found {len(products)} products")

        except Exception as e:
            print(f"[Bug] Error during search: {e}")

        return products

    def _parse_product_item(self, item) -> Optional[Dict]:
        """
        Parse a single product item from search results.

        Args:
            item: BeautifulSoup element

        Returns:
            Product data dictionary or None
        """
        try:
            # Product name
            name_elem = item.find('a', class_='product-title') or item.find('h3') or item.find('a', class_='title')
            if not name_elem:
                name_elem = item.find('div', class_='name')
            if not name_elem:
                return None

            product_name = name_elem.get_text(strip=True)

            # Product URL
            link_elem = item.find('a', href=True)
            product_link = link_elem.get('href', '') if link_elem else ''
            if product_link and not product_link.startswith('http'):
                product_link = f"{self.base_url}{product_link}"

            # Price
            price_elem = item.find('span', class_='price') or item.find('div', class_='price-box')
            if not price_elem:
                price_elem = item.find('span', attrs={'data-price': True})

            price = None
            if price_elem:
                price_text = price_elem.get('data-price') or price_elem.get_text(strip=True)
                price = self.extract_price(price_text)

            # Image
            img_elem = item.find('img', class_='product-img') or item.find('img')
            image_url = None
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-lazy-src')
                if image_url and not image_url.startswith('http'):
                    image_url = f"{self.base_url}{image_url}"

            # Availability
            availability = True
            availability_elem = item.find('span', class_='stock') or item.find('div', class_='availability')
            if availability_elem:
                availability_text = availability_elem.get_text(strip=True).lower()
                if 'אזל' in availability_text or 'לא זמין' in availability_text or 'out of stock' in availability_text:
                    availability = False

            # Rating
            rating = None
            rating_elem = item.find('div', class_='rating') or item.find('span', class_='stars')
            if rating_elem:
                rating_text = rating_elem.get('data-rating') or rating_elem.get_text(strip=True)
                try:
                    rating = float(''.join(c for c in rating_text if c.isdigit() or c == '.'))
                except ValueError:
                    pass

            return {
                'name': product_name,
                'url': product_link,
                'price': price,
                'image_url': image_url,
                'availability': availability,
                'rating': rating
            }

        except Exception as e:
            print(f"[Bug] Error parsing product item: {e}")
            return None

    def get_product_details(self, product_url: str) -> Optional[Dict]:
        """
        Get detailed information about a specific product from Bug.

        Args:
            product_url: URL of the product page

        Returns:
            Detailed product data or None
        """
        print(f"[Bug] Fetching details from: {product_url}")
        soup = self.get_page(product_url)

        if not soup:
            return None

        try:
            # Product name
            name_elem = soup.find('h1', class_='product-title') or soup.find('h1')
            product_name = name_elem.get_text(strip=True) if name_elem else 'Unknown'

            # Price
            price_elem = soup.find('span', class_='price-current') or soup.find('span', class_='final-price')
            price = None
            if price_elem:
                price_text = price_elem.get('data-price') or price_elem.get_text(strip=True)
                price = self.extract_price(price_text)

            # Old price (if on sale)
            old_price = None
            old_price_elem = soup.find('span', class_='price-old') or soup.find('span', class_='old-price')
            if old_price_elem:
                old_price_text = old_price_elem.get_text(strip=True)
                old_price = self.extract_price(old_price_text)

            # Description
            desc_elem = soup.find('div', class_='product-description') or soup.find('div', class_='description')
            description = None
            if desc_elem:
                # Remove script tags and clean up
                for script in desc_elem.find_all('script'):
                    script.decompose()
                description = desc_elem.get_text(strip=True)[:500]  # Limit to 500 chars

            # Main image
            img_elem = soup.find('img', class_='main-product-image') or soup.find('img', {'itemprop': 'image'})
            image_url = None
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = f"{self.base_url}{image_url}"

            # Availability
            availability = True
            availability_elem = soup.find('div', class_='stock-status') or soup.find('span', class_='availability')
            if availability_elem:
                availability_text = availability_elem.get_text(strip=True).lower()
                if 'אזל' in availability_text or 'לא זמין' in availability_text:
                    availability = False

            # Rating and reviews
            rating = None
            rating_elem = soup.find('div', class_='product-rating') or soup.find('span', {'itemprop': 'ratingValue'})
            if rating_elem:
                rating_text = rating_elem.get('content') or rating_elem.get_text(strip=True)
                try:
                    rating = float(''.join(c for c in rating_text if c.isdigit() or c == '.'))
                except ValueError:
                    pass

            review_count = 0
            review_elem = soup.find('span', {'itemprop': 'reviewCount'}) or soup.find('span', class_='review-count')
            if review_elem:
                review_text = review_elem.get('content') or review_elem.get_text(strip=True)
                try:
                    review_count = int(''.join(filter(str.isdigit, review_text)))
                except ValueError:
                    pass

            # Product code/SKU
            sku = None
            sku_elem = soup.find('span', class_='product-code') or soup.find('span', {'itemprop': 'sku'})
            if sku_elem:
                sku = sku_elem.get_text(strip=True)

            # Category
            category = None
            breadcrumb = soup.find('nav', class_='breadcrumb') or soup.find('div', class_='breadcrumbs')
            if breadcrumb:
                category_links = breadcrumb.find_all('a')
                if category_links:
                    category = category_links[-1].get_text(strip=True)

            return {
                'name': product_name,
                'description': description,
                'url': product_url,
                'image_url': image_url,
                'price': price,
                'old_price': old_price,
                'availability': availability,
                'rating': rating,
                'review_count': review_count,
                'sku': sku,
                'category': category,
                'on_sale': old_price is not None and old_price > price if price else False
            }

        except Exception as e:
            print(f"[Bug] Error getting product details: {e}")
            return None
