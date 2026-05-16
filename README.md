# Smart Price Comparison Platform

A full-stack price comparison web app for Israeli stores. Browse and compare prices across multiple retailers, with 3,000+ products in 8 categories and a Hebrew UI optimized for the Israeli market.

**[Live Demo](https://saharhalili95.github.io/price-comparison-platform/)**

## Features

- Automated product search and price tracking across multiple Israeli stores
- 3,000+ products across 8 categories
- Hebrew UI with responsive design
- End-to-end type safety with Pydantic (backend) and TypeScript (frontend)
- AI-accelerated development workflow with Cursor

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Frontend | React + TypeScript |
| Data Validation | Pydantic |
| Build Tool | Vite |

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser. The API runs at `http://localhost:8000`.

## License

MIT
