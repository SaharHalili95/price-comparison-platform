# 🕷️ מדריך Scrapers - גריפת מחירים מאתרים ישראליים

## 📋 סקירה כללית

המערכת כוללת scrapers מתקדמים שאוספים מידע אמיתי ממקורות ישראליים מובילים:

- **Zap.co.il** - אתר השוואת המחירים הפופולרי ביותר בישראל
- **KSP** - רשת אלקטרוניקה ומחשבים מובילה
- **Bug** - רשת אלקטרוניקה מובילה

## 🚀 מצבי הרצה

### 1. Mock Data (ברירת מחדל) - מהיר למפתחים
```bash
# מצב demo עם נתונים מדומים
# לא דורש התחברות לאינטרנט
# מהיר מאוד לפיתוח

curl "http://localhost:8001/api/products/search?query=mouse"
```

### 2. Real Scraping - נתונים אמיתיים
```bash
# גריפה אמיתית מהאתרים הישראליים
curl "http://localhost:8001/api/products/search?query=mouse&use_real_data=true"
```

## 📡 API Endpoints

### בדיקת סטטוס Scrapers
```bash
GET /api/scraper/status
```

**תגובה:**
```json
{
  "scrapers_available": true,
  "use_real_scrapers": false,
  "enabled_scrapers": ["zap", "ksp", "bug"],
  "message": "Using mock data"
}
```

### בדיקת Scrapers
```bash
POST /api/scraper/test?query=mouse
```

**תגובה:**
```json
{
  "query": "mouse",
  "results": {
    "zap": {
      "count": 3,
      "products": [...]
    },
    "ksp": {
      "count": 3,
      "products": [...]
    },
    "bug": {
      "count": 3,
      "products": [...]
    }
  },
  "total_products": 9
}
```

### חיפוש עם נתונים אמיתיים
```bash
GET /api/products/search?query=keyboard&use_real_data=true
```

## 🏗️ ארכיטקטורה

```
app/
└── scrapers/
    ├── __init__.py              # נקודת כניסה
    ├── base_scraper.py          # מחלקת בסיס עם פונקציות משותפות
    ├── zap_scraper.py           # Scraper ל-Zap
    ├── ksp_scraper.py           # Scraper ל-KSP
    ├── bug_scraper.py           # Scraper ל-Bug
    └── scraper_manager.py       # מנהל ומצרף תוצאות
```

## ⚙️ התקנה

### דרישות מקדימות
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### ספריות נדרשות
- `beautifulsoup4` - פרסור HTML
- `selenium` - אוטומציה של דפדפן
- `requests` - HTTP requests
- `lxml` - פרסור מהיר
- `fake-useragent` - User agents אקראיים
- `pandas` - עיבוד נתונים

## 🎯 שימוש ב-Python

### דוגמה פשוטה
```python
from app.scrapers.scraper_manager import ScraperManager

# יצירת מנהל scrapers
with ScraperManager() as manager:
    # חיפוש במקביל בכל האתרים
    results = manager.search_all_parallel("mouse", max_results_per_site=10)

    # צירוף התוצאות
    aggregated = manager.aggregate_results(results)

    # הדפסת התוצאות
    for product in aggregated:
        print(f"{product['name']}: ₪{product['lowest_price']}")
```

### שימוש ב-Scraper בודד
```python
from app.scrapers import ZapScraper

with ZapScraper() as zap:
    # חיפוש מוצרים
    products = zap.search_product("keyboard", max_results=5)

    # פרטים על מוצר
    if products:
        details = zap.get_product_details(products[0]['url'])
        print(details)
```

## 🛡️ שיקולי אבטחה וביצועים

### Rate Limiting
ה-scrapers כוללים מנגנוני rate limiting מובנים:
- השהיה אקראית בין 1-3 שניות בין requests
- Exponential backoff במקרה של שגיאה
- מקסימום 3 נסיונות חוזרים

### User Agents
כל scraper משתמש ב-user agents אקראיים כדי להימנע מחסימה.

### מקביליות
`ScraperManager` מריץ scrapers במקביל ל-performance טוב יותר:
```python
# מקביל (מהיר)
results = manager.search_all_parallel("mouse")

# סדרתי (יותר אמין)
results = manager.search_all_sequential("mouse")
```

## 📊 פורמט נתונים

### מוצר מצורף
```json
{
  "name": "Logitech MX Master 3",
  "description": "עכבר אלחוטי ארגונומי",
  "image_url": "https://...",
  "category": "Electronics",
  "prices": [
    {
      "source": "Zap",
      "price": 299.90,
      "currency": "ILS",
      "url": "https://...",
      "availability": true,
      "last_updated": "2026-01-13T..."
    },
    {
      "source": "KSP",
      "price": 319.00,
      "currency": "ILS",
      "url": "https://...",
      "availability": true,
      "last_updated": "2026-01-13T..."
    }
  ],
  "lowest_price": 299.90,
  "highest_price": 319.00,
  "average_price": 309.45,
  "potential_savings": 19.10,
  "savings_percent": 6.0
}
```

## 🐛 Debugging

### הפעלת logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# עכשיו תראה לוגים מפורטים של הscraping
```

### בדיקת scraper ספציפי
```bash
python -c "
from app.scrapers import ZapScraper
zap = ZapScraper()
results = zap.search_product('mouse', max_results=3)
for r in results:
    print(r['name'], r.get('price'))
"
```

## ⚠️ הערות חשובות

1. **שימוש אחראי** - אל תריצו scrapers בתדירות גבוהה מדי
2. **בדיקת robots.txt** - וודאו שאתם מכבדים את robots.txt של האתרים
3. **מבנה DOM משתנה** - האתרים משנים את המבנה מעת לעת, ה-scrapers עשויים לדרוש עדכון
4. **זמני תגובה** - scraping אמיתי איטי יותר ממוק data (3-10 שניות לחיפוש)

## 🔄 עדכון Scrapers

אם מבנה אתר השתנה, עדכנו את הסלקטורים ב:
- `zap_scraper.py` - שורות 35-50 (סלקטורי מוצרים)
- `ksp_scraper.py` - שורות 35-50
- `bug_scraper.py` - שורות 35-50

## 📈 שיפורים עתידיים

- [ ] הוספת caching לתוצאות
- [ ] שמירת תוצאות ל-database
- [ ] Scheduled scraping כל X שעות
- [ ] התראות על ירידות מחיר
- [ ] תמיכה באתרים נוספים (Amazon.com, eBay, etc.)
- [ ] API למעקב אחר היסטוריית מחירים

## 📞 תמיכה

נתקלתם בבעיה? בדקו את:
1. `/api/scraper/status` - האם ה-scrapers זמינים?
2. `/api/scraper/test` - האם ה-scrapers עובדים?
3. הלוגים בקונסול של הbackend

---

**נבנה עם ❤️ לקהילה הישראלית**
