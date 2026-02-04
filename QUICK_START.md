# Quick Start Guide

Get the Smart Price Comparison Platform running in under 5 minutes!

## Option 1: Try the Live Demo (Fastest! 🚀)

No installation required - just visit:

**[https://saharhalili95.github.io/price-comparison-platform/](https://saharhalili95.github.io/price-comparison-platform/)**

The live demo includes:
- 12 sample products with Israeli pricing
- Full search functionality
- Product categories you can click
- Responsive design with Hebrew support

## Option 2: Run Frontend Only (Quick)

Perfect for testing the UI without backend setup:

```bash
# Clone the repository
git clone https://github.com/SaharHalili95/price-comparison-platform.git
cd price-comparison-platform

# Install and run frontend
cd frontend
npm install
npm run dev
```

Frontend running at: `http://localhost:5173/price-comparison-platform/`

## Option 3: Full Stack Development (Complete)

Run both backend and frontend for full development environment:

### 1. Backend Setup (Terminal 1)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

Backend running at: `http://localhost:8001`
API Docs: `http://localhost:8001/docs`

### 2. Frontend Setup (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Frontend running at: `http://localhost:5173`

## Test It Out!

### With Live Demo:
1. Visit https://saharhalili95.github.io/price-comparison-platform/
2. Try searching for:
   - "iPhone" - finds iPhone 15 Pro Max
   - "PlayStation" - finds PS5 and Xbox
   - "אלקטרוניקה" - shows electronics category
   - "M3" - finds MacBook Pro M3
3. Click category buttons: אלקטרוניקה, מחשבים, גיימינג, etc.
4. View price comparisons from 3 stores

### With Local Setup:
1. Open `http://localhost:5173` (or `http://localhost:5173/price-comparison-platform/`)
2. Search for products
3. Click "Compare Prices" or "View Details" on any product

## Available Products in Demo

The demo includes these product categories:

### 📱 Electronics (אלקטרוניקה)
- iPhone 15 Pro Max
- Samsung Galaxy S24 Ultra

### 💻 Computers (מחשבים)
- MacBook Pro 14 M3 Pro
- Dell XPS 15

### 🎮 Gaming (גיימינג)
- PlayStation 5 Slim
- Xbox Series X
- Logitech G Pro Wireless Mouse

### 🏠 Home Appliances (מוצרי חשמל)
- Dyson V15 Detect
- iRobot Roomba j7+

### 🔌 Smart Home (בית חכם)
- Amazon Echo Dot
- Google Nest Hub
- Philips Hue Starter Kit

## Search Tips

- **English names work**: "iPhone", "PlayStation", "MacBook"
- **Hebrew works too**: "אלקטרוניקה", "מחשבים"
- **Partial matches**: "M3" finds MacBook M3
- **Categories**: Click the colorful category buttons
- **Empty search**: Shows all products

## Troubleshooting

### Live Demo
- If the site shows an old version, clear your browser cache (Ctrl+F5 / Cmd+Shift+R)
- Make sure JavaScript is enabled in your browser

### Local Setup - Frontend
- **Port already in use**: Vite will automatically try another port
- **Dependencies error**: Run `npm install` again
- **Build errors**: Make sure you're using Node.js 16+ (`node --version`)

### Local Setup - Backend
- **Port 8001 in use**: Change port in uvicorn command
- **Module not found**: Activate venv first (`source venv/bin/activate`)
- **Python version**: Requires Python 3.9+ (`python --version`)

## Next Steps

- **Customize**: Edit `frontend/src/data/mockProducts.ts` to add your own products
- **Deploy**: Push to GitHub and the site auto-deploys via GitHub Actions
- **Develop**: See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions
- **Explore**: Check API docs at `http://localhost:8001/docs` (if running backend)

## Quick Commands Reference

```bash
# Frontend only
cd frontend && npm install && npm run dev

# Frontend build
cd frontend && npm run build

# Backend only
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Run tests
cd backend && pytest tests/ -v

# Deploy to GitHub Pages
cd frontend && npm run deploy
```

That's it! You're ready to go! 🎉

For more detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)
