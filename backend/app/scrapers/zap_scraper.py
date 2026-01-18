"""
Zap.co.il Scraper
Israel's most popular price comparison website
"""

from typing import List, Dict, Optional
from urllib.parse import quote
from .base_scraper import BaseScraper


class ZapScraper(BaseScraper):
    """
    Scraper for Zap.co.il - Israel's leading price comparison platform
    """

    def __init__(self):
        super().__init__(
            site_name="Zap",
            base_url="https://www.zap.co.il"
        )
        self.search_url = f"{self.base_url}/search.aspx"

    def search_product(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for products on Zap.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of product dictionaries
        """
        products = []
        encoded_query = quote(query)
        search_url = f"{self.search_url}?keyword={encoded_query}"

        print(f"[Zap] Searching for: {query}")
        soup = self.get_page(search_url)

        if not soup:
            print(f"[Zap] Failed to fetch search results")
            return products

        try:
            # Zap uses different class names for product listings
            # This is a simplified version - actual implementation needs DOM inspection
            product_items = soup.find_all('div', class_='ProdBox', limit=max_results)

            if not product_items:
                # Try alternative selectors
                product_items = soup.find_all('div', class_='product-item', limit=max_results)

            for item in product_items:
                try:
                    product_data = self._parse_product_item(item)
                    if product_data:
                        products.append(self.format_product_data(product_data))
                except Exception as e:
                    print(f"[Zap] Error parsing product item: {e}")
                    continue

            print(f"[Zap] Found {len(products)} products")

        except Exception as e:
            print(f"[Zap] Error during search: {e}")

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
            name_elem = item.find('a', class_='ModelTitle') or item.find('h3')
            if not name_elem:
                return None
            product_name = name_elem.get_text(strip=True)

            # Product URL
            product_link = name_elem.get('href', '')
            if product_link and not product_link.startswith('http'):
                product_link = f"{self.base_url}{product_link}"

            # Price - Zap shows price range
            price_elem = item.find('span', class_='Price') or item.find('div', class_='price')
            price_text = price_elem.get_text(strip=True) if price_elem else None
            price = self.extract_price(price_text) if price_text else None

            # Image
            img_elem = item.find('img')
            image_url = img_elem.get('src', '') if img_elem else None
            if image_url and not image_url.startswith('http'):
                image_url = f"{self.base_url}{image_url}"

            # Store count (how many stores sell this item)
            store_count_elem = item.find('span', class_='NumOffers')
            store_count = 0
            if store_count_elem:
                count_text = store_count_elem.get_text(strip=True)
                try:
                    store_count = int(''.join(filter(str.isdigit, count_text)))
                except ValueError:
                    pass

            return {
                'name': product_name,
                'url': product_link,
                'price': price,
                'image_url': image_url,
                'store_count': store_count,
                'availability': True
            }

        except Exception as e:
            print(f"[Zap] Error parsing product item: {e}")
            return None

    def get_product_details(self, product_url: str) -> Optional[Dict]:
        """
        Get detailed information about a specific product from Zap.

        Args:
            product_url: URL of the product page

        Returns:
            Detailed product data or None
        """
        print(f"[Zap] Fetching details from: {product_url}")
        soup = self.get_page(product_url)

        if not soup:
            return None

        try:
            # Product name
            name_elem = soup.find('h1', class_='ModelTitle') or soup.find('h1')
            product_name = name_elem.get_text(strip=True) if name_elem else 'Unknown'

            # Description
            desc_elem = soup.find('div', class_='ModelDesc') or soup.find('div', class_='description')
            description = desc_elem.get_text(strip=True) if desc_elem else None

            # Main image
            img_elem = soup.find('img', class_='MainImg') or soup.find('img', {'itemprop': 'image'})
            image_url = img_elem.get('src', '') if img_elem else None
            if image_url and not image_url.startswith('http'):
                image_url = f"{self.base_url}{image_url}"

            # Price range from stores
            prices = []
            store_rows = soup.find_all('tr', class_='BizRow') or soup.find_all('div', class_='store-item')

            for row in store_rows[:10]:  # Limit to top 10 stores
                store_price_elem = row.find('span', class_='Price')
                if store_price_elem:
                    price = self.extract_price(store_price_elem.get_text(strip=True))
                    if price:
                        prices.append(price)

            # Calculate price statistics
            lowest_price = min(prices) if prices else None
            highest_price = max(prices) if prices else None
            average_price = sum(prices) / len(prices) if prices else None

            return {
                'name': product_name,
                'description': description,
                'url': product_url,
                'image_url': image_url,
                'price': lowest_price,  # Use lowest price as main price
                'lowest_price': lowest_price,
                'highest_price': highest_price,
                'average_price': round(average_price, 2) if average_price else None,
                'store_count': len(prices),
                'availability': len(prices) > 0
            }

        except Exception as e:
            print(f"[Zap] Error getting product details: {e}")
            return None

    def get_stores_for_product(self, product_url: str) -> List[Dict]:
        """
        Get list of stores selling this product with their prices.

        Args:
            product_url: URL of the product page

        Returns:
            List of store dictionaries with prices
        """
        soup = self.get_page(product_url)
        if not soup:
            return []

        stores = []
        store_rows = soup.find_all('tr', class_='BizRow') or soup.find_all('div', class_='store-item')

        for row in store_rows:
            try:
                # Store name
                store_name_elem = row.find('a', class_='BizName') or row.find('span', class_='store-name')
                store_name = store_name_elem.get_text(strip=True) if store_name_elem else 'Unknown'

                # Store price
                price_elem = row.find('span', class_='Price')
                price = self.extract_price(price_elem.get_text(strip=True)) if price_elem else None

                # Store link
                store_link_elem = row.find('a', class_='BuyNow') or row.find('a', {'target': '_blank'})
                store_url = store_link_elem.get('href', '') if store_link_elem else None

                if price:
                    stores.append({
                        'store_name': store_name,
                        'price': price,
                        'url': store_url,
                        'currency': 'ILS'
                    })

            except Exception as e:
                print(f"[Zap] Error parsing store row: {e}")
                continue

        return stores
