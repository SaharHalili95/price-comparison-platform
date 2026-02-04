# Smart Price Comparison Platform - Project Summary

## Overview

A full-stack web application that compares product prices from multiple online stores (Amazon, eBay, Walmart) to help users find the best deals. The application features a live demo deployed on GitHub Pages that runs entirely in the browser using mock data - no backend installation required!

🌐 **[Live Demo](https://saharhalili95.github.io/price-comparison-platform/)**

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Language**: Python 3.9+
- **Validation**: Pydantic 2.5.3
- **Database**: SQLAlchemy with SQLite (PostgreSQL ready)
- **Server**: Uvicorn with auto-reload
- **Documentation**: Auto-generated Swagger/OpenAPI

### Frontend
- **Framework**: React 18
- **Language**: TypeScript 5.3
- **Styling**: Tailwind CSS 3.4
- **Build Tool**: Vite 5.0
- **HTTP Client**: Axios 1.6

## Project Structure

```
price-comparison-platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py              # API endpoints
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # App configuration
│   │   │   └── database.py            # Database setup
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── product.py             # SQLAlchemy models
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── product.py             # Pydantic schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── scraper.py             # Price scraper/simulator
│   │   └── main.py                    # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   └── run.py                         # Convenience runner
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchBar.tsx          # Search interface
│   │   │   ├── ProductCard.tsx        # Product display card
│   │   │   ├── PriceComparisonTable.tsx  # Comparison table
│   │   │   └── Layout.tsx             # Page layout
│   │   ├── services/
│   │   │   └── api.ts                 # API client
│   │   ├── types/
│   │   │   └── product.ts             # TypeScript types
│   │   ├── styles/
│   │   │   └── index.css              # Global styles
│   │   ├── App.tsx                    # Main app component
│   │   └── main.tsx                   # Entry point
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── vite.config.ts
│   └── .gitignore
│
├── README.md                          # Project overview
├── SETUP_GUIDE.md                     # Detailed setup instructions
├── QUICK_START.md                     # Quick start guide
└── PROJECT_SUMMARY.md                 # This file
```

## Key Features Implemented

### Backend Features

1. **RESTful API with FastAPI**
   - Fast, modern Python web framework
   - Auto-generated OpenAPI/Swagger documentation
   - Type hints and validation

2. **Pydantic Data Validation**
   - Strict schema validation
   - Type safety
   - Automatic data serialization/deserialization
   - Custom validators (e.g., price must be > 0)

3. **Price Scraper/Simulator**
   - Simulates fetching prices from 3 sources
   - In production, would make real HTTP requests
   - Calculates price statistics (min, max, avg)
   - Random availability simulation

4. **Database Ready**
   - SQLAlchemy ORM
   - SQLite for development
   - PostgreSQL ready for production
   - Product model with timestamps

5. **CORS Configuration**
   - Allows frontend to communicate with backend
   - Configurable origins

6. **API Endpoints**
   - `GET /` - Health check
   - `GET /api/products/search?query={query}` - Search products
   - `GET /api/products/{id}` - Get product details
   - `GET /api/products/{id}/prices` - Get price comparison
   - `GET /api/products` - List all products

### Frontend Features

1. **Search Interface**
   - Real-time search bar
   - Popular search suggestions
   - Loading states
   - Error handling

2. **Product Cards**
   - Product image display
   - Price range visualization
   - Savings percentage badge
   - Category tags
   - Available sources display

3. **Price Comparison Table**
   - Detailed comparison view
   - Best price highlighting
   - Price statistics (min, max, avg)
   - Availability status
   - Direct store links
   - Savings calculator

4. **Responsive Design**
   - Mobile-friendly layout
   - Tailwind CSS utilities
   - Grid layout for product cards
   - Smooth transitions and hover effects

5. **TypeScript Integration**
   - Type-safe API calls
   - Interface definitions
   - Compile-time error checking

6. **Modern React Patterns**
   - Functional components
   - React Hooks (useState)
   - Component composition
   - Props drilling

## Data Flow

1. **User Search**
   - User enters search query in SearchBar
   - SearchBar calls `onSearch` callback
   - App component calls API service

2. **API Request**
   - Frontend `api.ts` makes HTTP request to backend
   - Backend receives request at `/api/products/search`
   - Query parameters validated by Pydantic

3. **Price Scraping**
   - Backend calls PriceScraper service
   - Scraper simulates fetching prices from 3 sources
   - Prices validated by Pydantic models
   - Statistics calculated

4. **Response**
   - Backend returns JSON response
   - Frontend receives SearchResponse
   - App component updates state
   - ProductCard components render

5. **Detail View**
   - User clicks "Compare Prices"
   - App shows PriceComparisonTable
   - Table displays all price information

## Pydantic Models

### PriceInfo
- source: SourceEnum (Amazon, eBay, Walmart)
- price: float (validated > 0)
- currency: str (default "USD")
- availability: bool
- url: Optional[str]
- last_updated: datetime

### ProductBase
- name: str (1-255 chars)
- description: Optional[str] (max 2000 chars)
- category: Optional[str] (max 100 chars)
- image_url: Optional[str]

### ProductWithPrices (extends ProductBase)
- id: int
- created_at: datetime
- updated_at: Optional[datetime]
- prices: List[PriceInfo]
- lowest_price: Optional[float]
- highest_price: Optional[float]
- average_price: Optional[float]

### SearchResponse
- query: str
- total_results: int
- products: List[ProductWithPrices]

## Sample Products

The live demo includes 12 sample products with Israeli pricing (₪):

### Electronics
1. iPhone 15 Pro Max 256GB - ₪4,999-5,399
2. Samsung Galaxy S24 Ultra 512GB - ₪4,599-4,999

### Computers
3. MacBook Pro 14 M3 Pro - ₪9,499-9,999
4. Dell XPS 15 - ₪7,999-8,499

### Gaming
5. PlayStation 5 Slim - ₪1,899-2,199
6. Xbox Series X - ₪1,799-2,099
7. Logitech G Pro Wireless Mouse - ₪449-549

### Home Appliances
8. Dyson V15 Detect - ₪2,299-2,699
9. iRobot Roomba j7+ - ₪2,499-2,899

### Smart Home
10. Amazon Echo Dot 5th Gen - ₪199-249
11. Google Nest Hub 2nd Gen - ₪399-499
12. Philips Hue Starter Kit - ₪499-599

## Testing the Application

### Manual Testing

1. **Health Check**
   ```bash
   curl http://localhost:8000/
   ```

2. **Search Products**
   ```bash
   curl "http://localhost:8000/api/products/search?query=mouse"
   ```

3. **Get Product Details**
   ```bash
   curl http://localhost:8000/api/products/1
   ```

### Frontend Testing

**Option 1: Test Live Demo**
1. Visit https://saharhalili95.github.io/price-comparison-platform/
2. Enter search term (e.g., "iPhone", "PlayStation")
3. View results
4. Click category buttons (אלקטרוניקה, מחשבים, גיימינג)
5. Verify price comparison display

**Option 2: Test Local Development**
1. Open http://localhost:5173/price-comparison-platform/
2. Enter search term
3. View results
4. Click "Compare Prices"
5. Verify price comparison table

## Development Workflow

### Adding New Products

Edit `backend/app/services/scraper.py`:

```python
SAMPLE_PRODUCTS.append({
    "id": 9,
    "name": "Your Product",
    "description": "Product description",
    "category": "Category",
    "image_url": "https://example.com/image.jpg",
    "base_price": 99.99
})
```

### Adding New Price Sources

1. Update `SourceEnum` in `backend/app/schemas/product.py`
2. Add source to `SOURCES` list in `backend/app/services/scraper.py`
3. Update `_generate_url` method
4. Update TypeScript enum in `frontend/src/types/product.ts`

### Customizing Styles

Tailwind CSS makes styling easy. Edit component classes or add custom styles in `frontend/src/styles/index.css`.

## Production Deployment

### Backend

1. Set environment variables
2. Use PostgreSQL database
3. Set DEBUG=False
4. Use Gunicorn with Uvicorn workers
5. Set up reverse proxy (Nginx)
6. Enable HTTPS

### Frontend

1. Build production bundle: `npm run build`
2. Serve static files from `dist/`
3. Configure environment variables
4. Set up CDN (optional)

### Hosting Options

- **Backend**: Heroku, DigitalOcean, AWS EC2, Google Cloud Run
- **Frontend**: GitHub Pages (current), Vercel, Netlify, AWS S3 + CloudFront
- **Database**: AWS RDS, DigitalOcean Managed Databases

### Current Deployment

The application is automatically deployed to GitHub Pages using GitHub Actions:
- **URL**: https://saharhalili95.github.io/price-comparison-platform/
- **Trigger**: Any push to `main` branch
- **Build**: Vite builds the React app with TypeScript
- **Deploy**: GitHub Actions deploys to `gh-pages` branch
- **Data**: Uses mock data stored in `frontend/src/data/mockProducts.ts`

## Future Enhancements

### Phase 1: Core Improvements
- [ ] Real web scraping implementation
- [ ] Database migrations with Alembic
- [ ] Unit tests (pytest for backend, Jest for frontend)
- [ ] Integration tests
- [ ] Error logging and monitoring

### Phase 2: User Features
- [ ] User authentication (JWT)
- [ ] Save favorite products
- [ ] Price alerts (email/push notifications)
- [ ] Price history charts
- [ ] Product reviews and ratings

### Phase 3: Advanced Features
- [ ] Price prediction using ML
- [ ] Browser extension
- [ ] Mobile app (React Native)
- [ ] Advanced filters and sorting
- [ ] Export comparison to PDF/CSV

### Phase 4: Scale
- [ ] Redis caching
- [ ] Rate limiting
- [ ] Background jobs (Celery)
- [ ] Microservices architecture
- [ ] GraphQL API

## Performance Considerations

### Backend
- Use async/await for I/O operations
- Implement caching (Redis)
- Database query optimization
- Connection pooling
- Rate limiting for scraping

### Frontend
- Code splitting
- Lazy loading components
- Image optimization
- Debounce search input
- Virtual scrolling for long lists

## Security Considerations

### Backend
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration
- Rate limiting
- Environment variables for secrets

### Frontend
- XSS prevention (React escapes by default)
- HTTPS only in production
- Secure API communication
- Content Security Policy

## Documentation

- **README.md**: Project overview and features
- **SETUP_GUIDE.md**: Detailed setup instructions
- **QUICK_START.md**: Quick start guide
- **PROJECT_SUMMARY.md**: This comprehensive summary
- **Swagger Docs**: Auto-generated API documentation at `/docs`

## License

MIT License - Free to use, modify, and distribute.

## Support

For questions or issues:
- Check the documentation files
- Review API docs at http://localhost:8000/docs
- Examine browser console for frontend errors
- Check terminal output for backend errors

---

**Built with FastAPI, React, TypeScript, and Tailwind CSS**
**Created for portfolio/CV demonstration**
