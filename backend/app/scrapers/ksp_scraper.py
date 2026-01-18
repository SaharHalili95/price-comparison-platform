"""
KSP Scraper
Major Israeli electronics and computer retail chain
"""

from typing import List, Dict, Optional
from urllib.parse import quote
from .base_scraper import BaseScraper


class KSPScraper(BaseScraper):
    """
    Scraper for KSP.co.il - Major Israeli electronics retailer
    """

    def __init__(self):
        super().__init__(
            site_name="KSP",
            base_url="https://ksp.co.il"
        )
        self.search_url = f"{self.base_url}/web/he/search"

    def search_product(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for products on KSP.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of product dictionaries
        """
        products = []
        encoded_query = quote(query)
        search_url = f"{self.search_url}?q={encoded_query}"

        print(f"[KSP] Searching for: {query}")
        soup = self.get_page(search_url)

        if not soup:
            print(f"[KSP] Failed to fetch search results")
            return products

        try:
            # KSP uses product cards in search results
            product_items = soup.find_all('div', class_='product-item', limit=max_results)

            if not product_items:
                # Try alternative selectors
                product_items = soup.find_all('div', class_='item', limit=max_results)
                if not product_items:
                    product_items = soup.find_all('div', attrs={'data-product-id': True}, limit=max_results)

            for item in product_items:
                try:
                    product_data = self._parse_product_item(item)
                    if product_data:
                        products.append(self.format_product_data(product_data))
                except Exception as e:
                    print(f"[KSP] Error parsing product item: {e}")
                    continue

            print(f"[KSP] Found {len(products)} products")

        except Exception as e:
            print(f"[KSP] Error during search: {e}")

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
            name_elem = item.find('a', class_='product-name') or item.find('h3') or item.find('a', class_='name')
            if not name_elem:
                return None
            product_name = name_elem.get_text(strip=True)

            # Product URL
            product_link = name_elem.get('href', '')
            if product_link and not product_link.startswith('http'):
                product_link = f"{self.base_url}{product_link}"

            # Price
            price_elem = item.find('span', class_='price') or item.find('div', class_='price-wrapper')
            if not price_elem:
                price_elem = item.find('span', attrs={'data-price': True})

            price = None
            if price_elem:
                price_text = price_elem.get('data-price') or price_elem.get_text(strip=True)
                price = self.extract_price(price_text)

            # Image
            img_elem = item.find('img', class_='product-image') or item.find('img')
            image_url = None
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = f"{self.base_url}{image_url}"

            # Availability
            availability_elem = item.find('span', class_='availability') or item.find('div', class_='stock')
            availability = True  # Default to available
            if availability_elem:
                availability_text = availability_elem.get_text(strip=True).lower()
                availability = 'במלאי' in availability_text or 'זמין' in availability_text or 'available' in availability_text

            # Product code/SKU
            sku_elem = item.find('span', class_='sku') or item.find('span', class_='product-code')
            sku = sku_elem.get_text(strip=True) if sku_elem else None

            return {
                'name': product_name,
                'url': product_link,
                'price': price,
                'image_url': image_url,
                'availability': availability,
                'sku': sku
            }

        except Exception as e:
            print(f"[KSP] Error parsing product item: {e}")
            return None

    def get_product_details(self, product_url: str) -> Optional[Dict]:
        """
        Get detailed information about a specific product from KSP.

        Args:
            product_url: URL of the product page

        Returns:
            Detailed product data or None
        """
        print(f"[KSP] Fetching details from: {product_url}")
        soup = self.get_page(product_url)

        if not soup:
            return None

        try:
            # Product name
            name_elem = soup.find('h1', class_='product-name') or soup.find('h1', class_='title')
            product_name = name_elem.get_text(strip=True) if name_elem else 'Unknown'

            # Price
            price_elem = soup.find('span', class_='price-value') or soup.find('span', attrs={'data-price': True})
            price = None
            if price_elem:
                price_text = price_elem.get('data-price') or price_elem.get_text(strip=True)
                price = self.extract_price(price_text)

            # Description
            desc_elem = soup.find('div', class_='product-description') or soup.find('div', class_='description')
            description = desc_elem.get_text(strip=True) if desc_elem else None

            # Main image
            img_elem = soup.find('img', class_='main-image') or soup.find('img', class_='product-image-main')
            image_url = None
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = f"{self.base_url}{image_url}"

            # Availability
            availability_elem = soup.find('span', class_='availability') or soup.find('div', class_='stock-status')
            availability = True
            if availability_elem:
                availability_text = availability_elem.get_text(strip=True).lower()
                availability = 'במלאי' in availability_text or 'זמין' in availability_text

            # Category
            category_elem = soup.find('div', class_='breadcrumbs') or soup.find('nav', class_='breadcrumb')
            category = None
            if category_elem:
                category_links = category_elem.find_all('a')
                if category_links:
                    category = category_links[-1].get_text(strip=True)

            # Specifications
            specs = {}
            spec_table = soup.find('table', class_='specifications') or soup.find('div', class_='specs')
            if spec_table:
                rows = spec_table.find_all('tr')
                for row in rows[:10]:  # Limit to first 10 specs
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 2:
                        key = cols[0].get_text(strip=True)
                        value = cols[1].get_text(strip=True)
                        specs[key] = value

            return {
                'name': product_name,
                'description': description,
                'url': product_url,
                'image_url': image_url,
                'price': price,
                'availability': availability,
                'category': category,
                'specifications': specs
            }

        except Exception as e:
            print(f"[KSP] Error getting product details: {e}")
            return None
