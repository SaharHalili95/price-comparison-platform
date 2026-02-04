# 🕷️ Scrapers Guide - Price Scraping from Israeli Websites

## 📋 Overview

The system includes advanced scrapers that collect real information from leading Israeli sources:

- **Zap.co.il** - Israel's most popular price comparison website
- **KSP** - Leading electronics and computer retail chain
- **Bug** - Leading electronics retail chain

**Note:** The live demo at [https://saharhalili95.github.io/price-comparison-platform/](https://saharhalili95.github.io/price-comparison-platform/) uses mock data and doesn't require scraping. This guide is for local development with the backend.

## 🚀 Operating Modes

### 1. Mock Data (Default) - Fast for Developers
```bash
# Demo mode with simulated data
# No internet connection required
# Very fast for development

curl "http://localhost:8001/api/products/search?query=mouse"
```

### 2. Real Scraping - Actual Data
```bash
# Real scraping from Israeli websites
curl "http://localhost:8001/api/products/search?query=mouse&use_real_data=true"
```

## 📡 API Endpoints

### Check Scrapers Status
```bash
GET /api/scraper/status
```

**Response:**
```json
{
  "scrapers_available": true,
  "use_real_scrapers": false,
  "enabled_scrapers": ["zap", "ksp", "bug"],
  "message": "Using mock data"
}
```

### Test Scrapers
```bash
POST /api/scraper/test?query=mouse
```

**Response:**
```json
{
  "query": "mouse",
  "results": {
    "zap": {
      "success": true,
      "products_found": 15,
      "response_time": "1.2s"
    },
    "ksp": {
      "success": true,
      "products_found": 8,
      "response_time": "0.9s"
    },
    "bug": {
      "success": true,
      "products_found": 12,
      "response_time": "1.1s"
    }
  }
}
```

## 🛠️ Scraper Implementation

### Architecture

Each scraper implements the `BaseScraper` interface:

```python
class BaseScraper:
    async def search(self, query: str) -> List[ProductData]:
        """Search for products"""
        pass

    async def get_product_prices(self, product_url: str) -> List[PriceInfo]:
        """Get prices for specific product"""
        pass
```

### Zap Scraper Example

```python
class ZapScraper(BaseScraper):
    BASE_URL = "https://www.zap.co.il"

    async def search(self, query: str):
        # Make HTTP request
        response = await self.client.get(
            f"{self.BASE_URL}/search",
            params={"q": query}
        )

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract products
        products = []
        for item in soup.select('.product-item'):
            product = self._parse_product(item)
            products.append(product)

        return products
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in `backend/` directory:

```env
# Scraper Settings
USE_REAL_SCRAPERS=false
SCRAPER_TIMEOUT=10
MAX_RETRIES=3

# Rate Limiting
REQUESTS_PER_MINUTE=30
CONCURRENT_REQUESTS=3

# User Agent
USER_AGENT=Mozilla/5.0 (compatible; PriceCompare/1.0)

# Proxy (optional)
# HTTP_PROXY=http://proxy.example.com:8080
# HTTPS_PROXY=https://proxy.example.com:8080
```

### Enabling Real Scrapers

```python
# In backend/app/core/config.py
class Settings(BaseSettings):
    USE_REAL_SCRAPERS: bool = False  # Set to True
```

## 🚦 Rate Limiting

To avoid getting blocked:

```python
# Configure rate limiter
RATE_LIMIT = {
    "requests_per_minute": 30,
    "concurrent_requests": 3,
    "delay_between_requests": 2  # seconds
}
```

## 🔄 Scraping Workflow

1. **User searches** for product
2. **API receives** search request
3. **Scraper Manager** distributes query to all scrapers
4. **Parallel scraping** from multiple sources
5. **Results aggregation** and deduplication
6. **Price analysis** (min, max, average)
7. **Return results** to frontend

## 📊 Mock Data vs Real Scraping

### Mock Data (Current Live Demo)
- ✅ Instant responses
- ✅ No external dependencies
- ✅ Consistent results
- ✅ No rate limiting issues
- ❌ Not real-time data

### Real Scraping (Backend Only)
- ✅ Real-time prices
- ✅ Actual product availability
- ✅ Real store links
- ❌ Slower responses (1-3 seconds)
- ❌ Requires rate limiting
- ❌ May get blocked without proper headers

## 🎯 Best Practices

### 1. Respect robots.txt
```python
# Check robots.txt before scraping
def can_scrape(url):
    robots = urllib.robotparser.RobotFileParser()
    robots.set_url(f"{url}/robots.txt")
    robots.read()
    return robots.can_fetch("*", url)
```

### 2. Use Proper Headers
```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PriceCompare/1.0)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}
```

### 3. Implement Caching
```python
# Cache results for 15 minutes
@cache(ttl=900)
async def search_products(query: str):
    return await scraper.search(query)
```

### 4. Handle Errors Gracefully
```python
try:
    results = await scraper.search(query)
except ScraperException as e:
    logger.error(f"Scraper failed: {e}")
    # Fall back to mock data
    results = get_mock_results(query)
```

## 🐛 Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Scrapers
```bash
# Test Zap scraper
curl "http://localhost:8001/api/scraper/test/zap?query=mouse"

# Test KSP scraper
curl "http://localhost:8001/api/scraper/test/ksp?query=mouse"

# Test Bug scraper
curl "http://localhost:8001/api/scraper/test/bug?query=mouse"
```

### Common Issues

#### 1. Blocked by Website
**Solution:** Implement rotating proxies and vary User-Agent strings

#### 2. HTML Structure Changed
**Solution:** Update CSS selectors in scraper code

#### 3. Rate Limited
**Solution:** Increase delay between requests, reduce concurrent requests

#### 4. Timeout Errors
**Solution:** Increase `SCRAPER_TIMEOUT` in settings

## 📈 Performance Optimization

### 1. Parallel Scraping
```python
# Scrape from multiple sources simultaneously
async def scrape_all(query: str):
    tasks = [
        zap_scraper.search(query),
        ksp_scraper.search(query),
        bug_scraper.search(query)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

### 2. Connection Pooling
```python
# Reuse HTTP connections
import httpx
client = httpx.AsyncClient(
    limits=httpx.Limits(max_connections=100)
)
```

### 3. Response Caching
```python
# Cache scraped data
from functools import lru_cache

@lru_cache(maxsize=1000)
def parse_product(html: str):
    return BeautifulSoup(html, 'html.parser')
```

## 🔐 Legal Considerations

- ⚖️ **Terms of Service:** Always check the website's ToS
- 🤖 **robots.txt:** Respect crawling rules
- 📜 **Rate Limits:** Don't overload servers
- 💰 **Commercial Use:** Some sites prohibit commercial scraping
- 📞 **Contact:** Consider reaching out for API access

## 🌐 Alternative: Official APIs

Many retailers offer official APIs:
- Better reliability
- Higher rate limits
- Legal compliance
- Structured data
- Support and documentation

**Recommendation:** Use official APIs when available instead of scraping.

## 📚 Additional Resources

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [httpx Documentation](https://www.python-httpx.org/)
- [Scrapy Framework](https://scrapy.org/) (for advanced scraping)
- [Web Scraping Best Practices](https://www.scrapingbee.com/blog/web-scraping-best-practices/)

## 🎓 Learning More

For the live demo, we use mock data stored in:
- `frontend/src/data/mockProducts.ts` - Product data with prices

This provides a fast, reliable demo without the complexity of real-time scraping.

---

**Note:** The live application at [https://saharhalili95.github.io/price-comparison-platform/](https://saharhalili95.github.io/price-comparison-platform/) uses mock data only. Real scraping is available when running the full backend locally.
