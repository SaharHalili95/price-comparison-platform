# Setup Guide - Smart Price Comparison Platform

This guide will help you set up and run the Smart Price Comparison Platform on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **npm** or **yarn** - Comes with Node.js

## Project Structure

```
price-comparison-platform/
├── backend/          # FastAPI backend
├── frontend/         # React + TypeScript frontend
├── README.md
└── SETUP_GUIDE.md
```

## Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create Environment File

```bash
cp .env.example .env
```

The default `.env` file uses SQLite. If you want to use PostgreSQL, update the `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgresql://username:password@localhost/dbname
```

### Step 5: Run the Backend Server

```bash
uvicorn app.main:app --reload
```

The backend will be available at:
- API: http://localhost:8000
- API Documentation (Swagger): http://localhost:8000/docs
- Alternative Documentation (ReDoc): http://localhost:8000/redoc

### Verify Backend is Running

Open your browser and go to http://localhost:8000/docs

You should see the interactive API documentation with all available endpoints.

## Frontend Setup

### Step 1: Open New Terminal

Keep the backend running and open a new terminal window/tab.

### Step 2: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 3: Install Dependencies

```bash
npm install
```

Or if you prefer yarn:
```bash
yarn install
```

### Step 4: Start Development Server

```bash
npm run dev
```

Or with yarn:
```bash
yarn dev
```

The frontend will be available at: http://localhost:5173

### Verify Frontend is Running

Open your browser and go to http://localhost:5173

You should see the Smart Price Comparison Platform homepage with a search bar.

## Testing the Application

### 1. Test Backend API

Visit http://localhost:8000/docs and try these endpoints:

- **GET /** - Health check
- **GET /api/products/search?query=mouse** - Search for products
- **GET /api/products/1** - Get product details
- **GET /api/products/1/prices** - Get price comparison

### 2. Test Frontend

1. Open http://localhost:5173
2. Enter a search term like "mouse" or "keyboard"
3. Click "Search" or press Enter
4. View product cards with price ranges
5. Click "Compare Prices" on any product to see detailed comparison

### Sample Search Queries

Try these search terms:
- `mouse`
- `keyboard`
- `headphones`
- `monitor`
- `webcam`
- `laptop stand`

## API Endpoints

### Health Check
```
GET /
GET /health
```

### Search Products
```
GET /api/products/search?query=mouse
```

### Get Product Details
```
GET /api/products/{product_id}
```

### Get Price Comparison
```
GET /api/products/{product_id}/prices
```

### List All Products
```
GET /api/products?category=Electronics&limit=10
```

## Features Implemented

### Backend Features
- FastAPI RESTful API
- Pydantic models for data validation
- Price scraper/simulator for 3 sources (Amazon, eBay, Walmart)
- Auto-generated Swagger documentation
- CORS support for frontend
- SQLite database (easily switchable to PostgreSQL)

### Frontend Features
- React 18 with TypeScript
- Tailwind CSS for styling
- Search functionality
- Product cards with price ranges
- Detailed price comparison table
- Responsive design
- Loading states and error handling

## Development Tips

### Backend Development

**Auto-reload on changes:**
The `--reload` flag enables auto-reload when you save files.

**View logs:**
All requests and errors are logged in the terminal where the backend is running.

**Add new products:**
Edit `backend/app/services/scraper.py` and add items to the `SAMPLE_PRODUCTS` list.

### Frontend Development

**Hot reload:**
Vite provides hot module replacement (HMR) - changes appear instantly.

**TypeScript checking:**
```bash
npm run build  # This runs TypeScript compiler
```

**Linting:**
```bash
npm run lint
```

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Or run on a different port
uvicorn app.main:app --reload --port 8001
```

**Import errors:**
Make sure your virtual environment is activated and all dependencies are installed:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Database errors:**
Delete the database file and restart:
```bash
rm price_comparison.db
```

### Frontend Issues

**Port 5173 already in use:**
Vite will automatically try the next available port (5174, 5175, etc.)

**Node modules issues:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**CORS errors:**
Make sure the backend is running and CORS is properly configured in `backend/app/main.py`

**API connection errors:**
- Verify backend is running at http://localhost:8000
- Check browser console for detailed error messages
- Ensure `frontend/src/services/api.ts` has correct API URL

## Building for Production

### Backend Production Build

1. Set `DEBUG=False` in `.env`
2. Use a production WSGI server:
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Production Build

```bash
cd frontend
npm run build
```

The built files will be in `frontend/dist/`

Serve with a static file server:
```bash
npm install -g serve
serve -s dist
```

## Next Steps

- Add user authentication
- Implement real web scraping (replace simulator)
- Add price history tracking
- Set up price alerts
- Add product categories
- Implement favorites/wishlist
- Add user reviews
- Deploy to production

## Support

For issues or questions:
- Check the [README.md](README.md) file
- Review the API documentation at http://localhost:8000/docs
- Check the browser console for frontend errors
- Check the terminal for backend errors

## License

MIT
