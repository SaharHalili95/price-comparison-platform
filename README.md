# PriceCompare Pro - Smart Price Comparison Platform

![CI](https://github.com/SaharHalili95/price-comparison-platform/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

פלטפורמה מתקדמת להשוואת מחירים עם תמיכה מלאה באתרים ישראליים מובילים: **Zap, KSP ו-Bug**.

## ✨ תכונות מרכזיות

- 🔍 **חיפוש חכם** - חפשו מוצרים ממספר מקורות במקביל
- 💰 **השוואת מחירים בזמן אמת** - קבלו מחירים עדכניים מכל החנויות
- 📊 **ניתוח מחירים** - מחיר מינימום, מקסימום וממוצע
- 🚀 **ביצועים גבוהים** - Scraping מקבילי ל-results מהירים
- 🎨 **UI מודרני** - עיצוב מרשים עם Tailwind CSS וגרדיאנטים
- 🇮🇱 **תמיכה בעברית** - ממשק מלא בעברית עם RTL
- 🤖 **Mock & Real Data** - מצב demo מהיר ומצב scraping אמיתי

## 🚀 הרצה מהירה

```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Frontend
cd frontend && npm run dev
```

**גישה:**
- Frontend: http://localhost:5173
- API: http://localhost:8001
- Docs: http://localhost:8001/docs

## 📡 דוגמאות שימוש

### חיפוש רגיל (mock data)
```bash
curl "http://localhost:8001/api/products/search?query=mouse"
```

### חיפוש עם נתונים אמיתיים
```bash
curl "http://localhost:8001/api/products/search?query=mouse&use_real_data=true"
```

למידע מפורט: [SCRAPERS_GUIDE.md](./SCRAPERS_GUIDE.md)

## Docker

Run the entire application with Docker:

```bash
docker-compose up --build
```

This will start:
- Backend API at `http://localhost:8001`
- Frontend at `http://localhost:5173`

## Testing

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

---

**נבנה עם ❤️ בישראל**
