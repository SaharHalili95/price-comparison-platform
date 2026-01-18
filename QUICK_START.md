# Quick Start Guide

Get the Smart Price Comparison Platform running in 5 minutes!

## 1. Backend Setup (Terminal 1)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Backend running at: http://localhost:8000
API Docs: http://localhost:8000/docs

## 2. Frontend Setup (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Frontend running at: http://localhost:5173

## 3. Test It Out!

1. Open http://localhost:5173
2. Search for "mouse" or "keyboard"
3. Click "Compare Prices" on any product

## Available Search Terms

- mouse
- keyboard
- headphones
- monitor
- webcam
- laptop
- SSD

That's it! You're ready to go!

For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)
