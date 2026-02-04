# PriceCompare Pro - Smart Price Comparison Platform

![CI](https://github.com/SaharHalili95/price-comparison-platform/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

🌐 **[Live Demo](https://saharhalili95.github.io/price-comparison-platform/)**

A modern price comparison web application built with React + TypeScript frontend and FastAPI backend. The live demo runs entirely in the browser using mock data - no backend installation required!

## ✨ Key Features

- 🔍 **Smart Search** - Search products across multiple sources in parallel
- 💰 **Real-Time Price Comparison** - Get up-to-date prices from all stores
- 📊 **Price Analysis** - View minimum, maximum, and average prices
- 🚀 **High Performance** - Parallel scraping for fast results
- 🎨 **Modern UI** - Beautiful design with Tailwind CSS and gradients
- 🇮🇱 **Hebrew Support** - Full Hebrew interface with RTL support
- 🤖 **Mock & Real Data** - Quick demo mode and real scraping mode

## 🚀 Live Demo

Visit the live application: **[https://saharhalili95.github.io/price-comparison-platform/](https://saharhalili95.github.io/price-comparison-platform/)**

The demo includes:
- 12 sample products with realistic Israeli pricing
- Full search functionality
- Product categories (Electronics, Computers, Gaming, Home & Smart Home)
- Price comparison from 3 stores (Amazon, eBay, Walmart)
- Responsive design with Hebrew RTL support

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework

### Backend (Optional for local development)
- **FastAPI** - High-performance Python web framework
- **Pydantic** - Data validation and settings management
- **BeautifulSoup4** - Web scraping
- **Python 3.11+** - Modern Python features

## 📦 Quick Start

### Option 1: View Live Demo (Recommended)
Simply visit: [https://saharhalili95.github.io/price-comparison-platform/](https://saharhalili95.github.io/price-comparison-platform/)

### Option 2: Run Locally (Frontend Only)

```bash
# Clone the repository
git clone https://github.com/SaharHalili95/price-comparison-platform.git
cd price-comparison-platform

# Install and run frontend
cd frontend
npm install
npm run dev
```

Access at: `http://localhost:5173/price-comparison-platform/`

### Option 3: Full Stack Development

```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

**Access Points:**
- Frontend: http://localhost:5173
- API: http://localhost:8001
- API Docs: http://localhost:8001/docs

## 📡 API Usage Examples

### Search with Mock Data
```bash
curl "http://localhost:8001/api/products/search?query=mouse"
```

### Search with Real Data (Requires Backend)
```bash
curl "http://localhost:8001/api/products/search?query=mouse&use_real_data=true"
```

For detailed information: [SCRAPERS_GUIDE.md](./SCRAPERS_GUIDE.md)

## 🐳 Docker Deployment

Run the entire application with Docker:

```bash
docker-compose up --build
```

This will start:
- Backend API at `http://localhost:8001`
- Frontend at `http://localhost:5173`

## 🧪 Testing

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

## 📁 Project Structure

```
price-comparison-platform/
├── frontend/                # React + TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── data/          # Mock data for demo
│   │   ├── services/      # API service layer
│   │   ├── types/         # TypeScript type definitions
│   │   └── App.tsx        # Main application component
│   ├── dist/              # Build output
│   └── package.json       # Dependencies and scripts
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── main.py       # FastAPI application
│   │   ├── scrapers/     # Web scraping modules
│   │   └── models/       # Data models
│   └── requirements.txt   # Python dependencies
└── README.md             # This file
```

## 🚀 Deployment

The application is automatically deployed to GitHub Pages using GitHub Actions. Any push to the `main` branch triggers a new deployment.

### Manual Deployment

```bash
cd frontend
npm run build
npm run deploy
```

## 🌟 Sample Products

The demo includes these product categories:

- **Electronics**: iPhone 15 Pro Max, Samsung Galaxy S24 Ultra
- **Computers**: MacBook Pro M3, Dell XPS 15
- **Gaming**: PlayStation 5, Xbox Series X, Gaming peripherals
- **Smart Home**: Amazon Echo, Google Nest, Philips Hue

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Sahar Halili**
- GitHub: [@SaharHalili95](https://github.com/SaharHalili95)
- Email: sahar_halili@icloud.com

---

**Built with ❤️ in Israel**
