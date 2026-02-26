# PriceCompare Pro - Smart Price Comparison Platform

![CI](https://github.com/SaharHalili95/price-comparison-platform/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)
![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Auth](https://img.shields.io/badge/auth-Zero%20Trust-red.svg)

🌐 **[Live Demo](https://saharhalili95.github.io/price-comparison-platform/)**

A modern price comparison web application built with React + TypeScript frontend and FastAPI backend, secured with a **Zero Trust Authentication** system. Every API request is verified, tokens are short-lived and rotated, and all auth events are audited.

## ✨ Key Features

- 🔐 **Zero Trust Authentication** - JWT-based auth with token rotation, blacklisting, and audit logging
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
- User registration and login (Zero Trust Authentication)
- 12 sample products with realistic Israeli pricing
- Full search functionality
- Product categories (Electronics, Computers, Gaming, Home & Smart Home)
- Price comparison from 3 stores (Amazon, eBay, Walmart)
- Responsive design with Hebrew RTL support

## 🔐 Zero Trust Authentication

This project implements a full Zero Trust security model — **never trust, always verify**.

| Feature | Details |
|---------|---------|
| **JWT Tokens** | Access (15 min) + Refresh (7 days) with automatic rotation |
| **Token Rotation** | Refresh tokens are single-use; each refresh issues a new pair |
| **Token Revocation** | Blacklist table for immediate logout across all devices |
| **Account Lockout** | 5 failed login attempts = 30 minute lock |
| **Rate Limiting** | Per-IP limits on all auth endpoints (slowapi) |
| **RBAC** | User/Admin roles with admin-only endpoints |
| **Audit Logging** | All auth events logged with IP, user-agent, timestamp |
| **Device Tracking** | IP + User-Agent recorded per session |
| **Security Headers** | HSTS, X-Frame-Options, X-Content-Type-Options, CSP |
| **Password Security** | bcrypt (12 rounds) + strength validation (uppercase, lowercase, digit, 8+ chars) |
| **Input Validation** | Pydantic schemas with strict rules on all endpoints |

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router v6** - Client-side routing with protected routes

### Backend
- **FastAPI** - High-performance Python web framework
- **Pydantic** - Data validation and settings management
- **SQLAlchemy** - ORM with SQLite database
- **python-jose** - JWT token creation and validation
- **passlib + bcrypt** - Password hashing
- **slowapi** - Rate limiting
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

### Register a New User
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "user1", "password": "MyPass123", "full_name": "Test User"}'
```

### Login
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "MyPass123"}'
```

### Search Products (Authenticated)
```bash
curl "http://localhost:8001/api/products/search?query=mouse" \
  -H "Authorization: Bearer <access_token>"
```

### Refresh Token
```bash
curl -X POST http://localhost:8001/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

For detailed scraping information: [SCRAPERS_GUIDE.md](./SCRAPERS_GUIDE.md)

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
├── frontend/                    # React + TypeScript frontend
│   ├── src/
│   │   ├── components/         # React components (Layout, ProtectedRoute)
│   │   ├── contexts/           # AuthContext (login/register/logout state)
│   │   ├── pages/              # LoginPage, RegisterPage, HomePage
│   │   ├── services/           # API layer (authApi, api)
│   │   ├── types/              # TypeScript types (auth, products)
│   │   ├── data/               # Mock data for demo
│   │   └── App.tsx             # Router with protected routes
│   └── package.json
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py       # Product endpoints (protected)
│   │   │   └── auth_routes.py  # Auth endpoints (register/login/refresh/logout)
│   │   ├── core/
│   │   │   ├── config.py       # Settings (JWT, rate limits, lockout)
│   │   │   ├── security.py     # JWT creation/validation, bcrypt hashing
│   │   │   ├── dependencies.py # get_current_user, require_admin
│   │   │   ├── rate_limiter.py # slowapi per-IP limiter
│   │   │   └── middleware.py   # Security headers middleware
│   │   ├── models/             # SQLAlchemy models (User, Session, TokenBlacklist, AuditLog)
│   │   ├── schemas/            # Pydantic validation schemas
│   │   ├── services/           # Business logic (AuthService)
│   │   ├── scrapers/           # Web scraping modules
│   │   └── main.py             # FastAPI app entry point
│   └── requirements.txt
└── README.md
```

## 🚀 Deployment

The application is automatically deployed to GitHub Pages using GitHub Actions. Any push to the `main` branch triggers a new deployment.

### Manual Deployment

```bash
cd frontend
npm run build
npm run deploy
```

## 🔑 Auth Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:---:|
| POST | `/api/auth/register` | Create new account | No |
| POST | `/api/auth/login` | Get access + refresh tokens | No |
| POST | `/api/auth/refresh` | Rotate refresh token | No |
| POST | `/api/auth/logout` | Revoke tokens | Yes |
| GET | `/api/auth/me` | Get current user profile | Yes |

All product endpoints (`/api/products/*`) require authentication. Admin endpoints (`scraper_status`, `test_scrapers`) require the `admin` role.

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
