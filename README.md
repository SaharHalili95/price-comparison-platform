# 🛒 PriceCompare Pro - פלטפורמת השוואת מחירים חכמה

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Israeli_Sites-orange.svg)

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

---

**נבנה עם ❤️ בישראל**
