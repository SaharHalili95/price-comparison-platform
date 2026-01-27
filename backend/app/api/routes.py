from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional
from app.schemas.product import ProductWithPrices, SearchResponse, PriceInfo
from app.services.scraper import PriceScraper
from app.data.products_database import search_products, get_products_by_category, get_categories, get_category_stats, get_all_products
from datetime import datetime
import os

# Import real scrapers if available
try:
    from app.scrapers.scraper_manager import ScraperManager
    SCRAPERS_AVAILABLE = True
except ImportError:
    SCRAPERS_AVAILABLE = False
    print("[API] Warning: Real scrapers not available, using mock data")

router = APIRouter(prefix="/api", tags=["products"])
mock_scraper = PriceScraper()

# Use real scrapers if enabled via environment variable
USE_REAL_SCRAPERS = os.getenv("USE_REAL_SCRAPERS", "false").lower() == "true"


def get_scraper_manager():
    """Get scraper manager instance"""
    if USE_REAL_SCRAPERS and SCRAPERS_AVAILABLE:
        return ScraperManager()
    return None


@router.get("/products/search", response_model=SearchResponse)
async def search_products_endpoint(
    query: str = Query(..., min_length=1, description="Search query for products"),
    category: Optional[str] = Query(None, description="Filter by category"),
    use_real_data: bool = Query(False, description="Use real scraping (slower but accurate)")
):
    """
    Search for products by name.
    Returns products with price comparison from multiple sources.

    Set use_real_data=true to scrape real Israeli sites (Zap, KSP, Bug).
    Default uses fast mock data for demo purposes.
    """

    if use_real_data and SCRAPERS_AVAILABLE:
        # Use real scrapers
        print(f"[API] Using REAL scrapers for query: {query}")

        with ScraperManager() as manager:
            # Search all sites in parallel
            scraper_results = manager.search_all_parallel(query, max_results_per_site=5)

            # Aggregate results
            aggregated_products = manager.aggregate_results(scraper_results)

            # Convert to API response format
            products_with_prices = []
            for idx, product in enumerate(aggregated_products[:10], start=1):  # Limit to 10
                product_with_prices = ProductWithPrices(
                    id=idx,
                    name=product.get('name', ''),
                    description=product.get('description'),
                    category=product.get('category'),
                    image_url=product.get('image_url'),
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    prices=product.get('prices', []),
                    lowest_price=product.get('lowest_price'),
                    highest_price=product.get('highest_price'),
                    average_price=product.get('average_price')
                )
                products_with_prices.append(product_with_prices)

            return SearchResponse(
                query=query,
                total_results=len(products_with_prices),
                products=products_with_prices
            )

    else:
        # Use mock data (fast for demo) with 3000 products database
        print(f"[API] Using MOCK data for query: {query}, category: {category}")

        # Search in the large products database
        matching_products = search_products(query, category=category)

        # Limit results to 50 for performance
        matching_products = matching_products[:50]

        # Add price information to each product
        products_with_prices = []
        for product in matching_products:
            prices = mock_scraper.scrape_prices(product["name"], product.get("base_price"))
            price_stats = mock_scraper.get_price_statistics(prices)

            product_with_prices = ProductWithPrices(
                id=product["id"],
                name=product["name"],
                description=product["description"],
                category=product["category"],
                image_url=product["image_url"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                prices=prices,
                **price_stats
            )
            products_with_prices.append(product_with_prices)

        return SearchResponse(
            query=query,
            total_results=len(products_with_prices),
            products=products_with_prices
        )


@router.get("/products/{product_id}", response_model=ProductWithPrices)
async def get_product(product_id: int):
    """
    Get a specific product by ID with price comparison.
    """
    products = get_all_products()

    # Find product by ID
    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get prices from different sources
    prices = mock_scraper.scrape_prices(product["name"], product.get("base_price"))
    price_stats = mock_scraper.get_price_statistics(prices)

    return ProductWithPrices(
        id=product["id"],
        name=product["name"],
        description=product["description"],
        category=product["category"],
        image_url=product["image_url"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        prices=prices,
        **price_stats
    )


@router.get("/products/{product_id}/prices", response_model=List[PriceInfo])
async def get_product_prices(product_id: int):
    """
    Get price comparison for a specific product.
    Returns prices from all available sources.
    """
    products = get_all_products()

    # Find product by ID
    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get prices from different sources
    prices = mock_scraper.scrape_prices(product["name"], product.get("base_price"))

    return prices


@router.get("/products", response_model=List[ProductWithPrices])
async def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=100, description="Number of products to return")
):
    """
    List all products with price comparison.
    Optionally filter by category.
    """
    products = get_all_products()

    # Filter by category if provided
    if category:
        products = [p for p in products if p["category"].lower() == category.lower()]

    # Limit results
    products = products[:limit]

    # Add price information to each product
    products_with_prices = []
    for product in products:
        prices = mock_scraper.scrape_prices(product["name"], product.get("base_price"))
        price_stats = mock_scraper.get_price_statistics(prices)

        product_with_prices = ProductWithPrices(
            id=product["id"],
            name=product["name"],
            description=product["description"],
            category=product["category"],
            image_url=product["image_url"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            prices=prices,
            **price_stats
        )
        products_with_prices.append(product_with_prices)

    return products_with_prices


@router.get("/categories")
async def list_categories():
    """
    Get list of all available categories.
    """
    categories = get_categories()
    stats = get_category_stats()
    return {
        "categories": categories,
        "stats": stats,
        "total_categories": len(categories)
    }


@router.get("/categories/{category_name}/products", response_model=SearchResponse)
async def get_category_products(
    category_name: str,
    limit: int = Query(50, ge=1, le=100, description="Number of products to return")
):
    """
    Get all products in a specific category.
    """
    # Get products from category
    products = get_products_by_category(category_name, limit=limit)

    if not products:
        return SearchResponse(
            query=category_name,
            total_results=0,
            products=[]
        )

    # Add price information to each product
    products_with_prices = []
    for product in products:
        prices = mock_scraper.scrape_prices(product["name"], product.get("base_price"))
        price_stats = mock_scraper.get_price_statistics(prices)

        product_with_prices = ProductWithPrices(
            id=product["id"],
            name=product["name"],
            description=product["description"],
            category=product["category"],
            image_url=product["image_url"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            prices=prices,
            **price_stats
        )
        products_with_prices.append(product_with_prices)

    return SearchResponse(
        query=category_name,
        total_results=len(products_with_prices),
        products=products_with_prices
    )


@router.get("/scraper/status")
async def scraper_status():
    """
    Get status of real scrapers.
    """
    return {
        "scrapers_available": SCRAPERS_AVAILABLE,
        "use_real_scrapers": USE_REAL_SCRAPERS,
        "enabled_scrapers": ["zap", "ksp", "bug"] if SCRAPERS_AVAILABLE else [],
        "message": "Real scrapers active" if USE_REAL_SCRAPERS and SCRAPERS_AVAILABLE else "Using mock data"
    }


@router.post("/scraper/test")
async def test_scrapers(query: str = Query("mouse", description="Test query")):
    """
    Test real scrapers with a query.
    This endpoint always uses real scraping.
    """
    if not SCRAPERS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Real scrapers not available. Install required packages: beautifulsoup4, selenium, requests"
        )

    with ScraperManager() as manager:
        results = manager.search_all_parallel(query, max_results_per_site=3)

        # Format results for response
        formatted_results = {}
        for scraper_name, products in results.items():
            formatted_results[scraper_name] = {
                "count": len(products),
                "products": products[:3]  # Return top 3 from each
            }

        return {
            "query": query,
            "results": formatted_results,
            "total_products": sum(len(p) for p in results.values())
        }
