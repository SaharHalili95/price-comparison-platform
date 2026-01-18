"""
Large products database with 3000+ products across multiple categories
"""

import random

# Product templates by category with English keywords
CATEGORIES = {
    "אלקטרוניקה": {
        "brands": ["Apple", "Samsung", "Sony", "LG", "Philips", "HP", "Dell", "Lenovo", "Asus", "Acer"],
        "products": [
            {"he": "טלפון סלולרי", "en": "phone smartphone mobile cellphone"},
            {"he": "מחשב נייד", "en": "laptop notebook computer"},
            {"he": "טאבלט", "en": "tablet ipad"},
            {"he": "אוזניות", "en": "headphones earphones earbuds headset"},
            {"he": "רמקול Bluetooth", "en": "speaker bluetooth wireless"},
            {"he": "מסך מחשב", "en": "monitor display screen"},
            {"he": "מקלדת", "en": "keyboard"},
            {"he": "עכבר", "en": "mouse"},
            {"he": "מצלמת רשת", "en": "webcam camera"},
            {"he": "מטען נייד", "en": "powerbank charger portable"},
            {"he": "כונן חיצוני", "en": "external drive harddrive hdd"},
            {"he": "זיכרון USB", "en": "usb flash drive stick"},
            {"he": "כרטיס זיכרון", "en": "memory card sd microsd"},
            {"he": "מתאם USB-C", "en": "adapter usb-c hub"},
            {"he": "מטען אלחוטי", "en": "wireless charger"},
            {"he": "שעון חכם", "en": "smartwatch watch"},
            {"he": "צמיד כושר", "en": "fitness tracker band"},
            {"he": "טלוויזיה חכמה", "en": "smart tv television"},
            {"he": "סאונדבר", "en": "soundbar speaker"},
            {"he": "קונסולת משחקים", "en": "gaming console playstation xbox"},
            {"he": "בקר משחק", "en": "controller gamepad joystick"},
            {"he": "מצלמה דיגיטלית", "en": "camera digital"}
        ]
    },
    "מחשבים": {
        "brands": ["Intel", "AMD", "Nvidia", "Corsair", "Kingston", "Western Digital", "Seagate", "Logitech"],
        "products": [
            "מעבד", "כרטיס מסך", "לוח אם", "זיכרון RAM", "SSD", "HDD",
            "ספק כח", "מארז מחשב", "מאוורר", "קירור נוזלי", "משחק מחשב",
            "מקלדת גיימינג", "עכבר גיימינג", "משטח עכבר", "אוזניות גיימינג",
            "מיקרופון", "מצלמת רשת HD", "כיסא גיימינג", "שולחן גיימינג"
        ]
    },
    "בית וגן": {
        "brands": ["Ikea", "Xiaomi", "Philips", "Osram", "Bosch", "Black&Decker", "Makita"],
        "products": [
            "נורת LED חכמה", "מנורת שולחן", "מנורת עמידה", "שואב אבק רובוטי",
            "שואב אבק אלחוטי", "מכונת כביסה", "מייבש כביסה", "מדיח כלים",
            "מקרר", "תנור חימום", "מזגן", "מפזר ריח", "מטהר אוויר",
            "מכשיר אדים", "מאוורר", "מנורת קריאה", "גריל חשמלי",
            "מכונת קפה", "קומקום חשמלי", "טוסטר", "מיקסר"
        ]
    },
    "ספורט ובריאות": {
        "brands": ["Nike", "Adidas", "Under Armour", "Reebok", "Puma", "Fitbit", "Garmin"],
        "products": [
            "נעלי ריצה", "בגדי ספורט", "מזרן יוגה", "משקולות", "רצועות התנגדות",
            "כדור פיזיו", "חבל קפיצה", "כפפות אימון", "חגורת כושר", "בקבוק שתייה",
            "שעון ספורט", "אוזניות ספורט", "תיק ספורט", "מגן ברכיים",
            "סוגר מרפק", "סוגר פרק כף יד", "רולר עיסוי", "כדור עיסוי"
        ]
    },
    "אופנה": {
        "brands": ["Zara", "H&M", "Mango", "Castro", "Fox", "Renuar", "Golf"],
        "products": [
            "חולצת טי שירט", "חולצה מכופתרת", "ג'ינס", "מכנסיים", "שמלה",
            "חצאית", "ז'קט", "מעיל", "סווטשירט", "הודי", "נעליים",
            "נעלי ספורט", "סנדלים", "מגפיים", "תיק יד", "תיק גב",
            "ארנק", "חגורה", "כובע", "משקפי שמש", "שעון יד", "צמיד"
        ]
    },
    "ילדים ותינוקות": {
        "brands": ["Pampers", "Huggies", "Chicco", "Fisher-Price", "Lego", "Mattel"],
        "products": [
            "חיתולים", "מגבונים לחים", "קרם ישבן", "שמפו לתינוקות", "סבון רחצה",
            "עגלת תינוק", "סלקל לרכב", "כיסא אוכל", "מיטת תינוק", "מזרן לתינוק",
            "פעמון", "שלשלת לעגלה", "משחק התפתחות", "לגו", "בובה", "רכב צעצוע",
            "פאזל", "משחק קופסה", "צעצוע אמבט", "מדחום תינוקות", "בקבוק הזנה"
        ]
    },
    "מזון ושתייה": {
        "brands": ["Osem", "Telma", "Elite", "Strauss", "Tnuva", "Coca Cola"],
        "products": [
            "שוקולד", "ביסקוויטים", "חטיף בריאות", "אגוזים", "פירות יבשים",
            "דגני בוקר", "פסטה", "רוטב עגבניות", "שמן זית", "קפה",
            "תה", "משקה קל", "מיץ פירות", "מים מינרלים", "חטיף חלבון",
            "חמאת בוטנים", "ריבה", "דבש", "שוקולד למריחה", "דייסת שיבולת שועל"
        ]
    },
    "טיפוח ויופי": {
        "brands": ["L'Oreal", "Nivea", "Garnier", "Dove", "Maybelline", "Revlon"],
        "products": [
            "קרם פנים", "קרם לחות", "קרם יום", "קרם לילה", "סרום פנים",
            "תחליב גוף", "מסכת פנים", "מים מיסליארים", "טונר", "קרם עיניים",
            "שמפו", "מרכך שיער", "מסכת שיער", "ג'ל עיצוב", "ספריי שיער",
            "אודם", "מסקרה", "צל עיניים", "ליינר", "מייק אפ", "קרם BB"
        ]
    }
}

def generate_products_database(total_products=3000):
    """Generate a large database of products"""
    products = []
    product_id = 1

    # Calculate products per category
    categories_list = list(CATEGORIES.keys())
    products_per_category = total_products // len(categories_list)

    for category_name in categories_list:
        category_data = CATEGORIES[category_name]
        brands = category_data["brands"]
        product_types = category_data["products"]

        # Generate products for this category
        for i in range(products_per_category):
            brand = random.choice(brands)
            product_type = random.choice(product_types)

            # Handle both dict and string product types
            if isinstance(product_type, dict):
                product_name_he = product_type["he"]
                product_keywords_en = product_type["en"]
            else:
                product_name_he = product_type
                product_keywords_en = product_type

            # Create unique product names
            if i % 3 == 0:
                name = f"{brand} {product_name_he} Pro"
            elif i % 3 == 1:
                name = f"{brand} {product_name_he} {random.choice(['Max', 'Plus', 'Ultra', 'Lite', 'Air'])}"
            else:
                name = f"{product_name_he} {brand}"

            # Add model number sometimes
            if random.random() > 0.5:
                name += f" {random.randint(100, 999)}"

            # Add English keywords to description for search
            search_keywords = f"{brand} {product_keywords_en}" if isinstance(product_type, dict) else brand

            # Generate base price based on category
            price_ranges = {
                "אלקטרוניקה": (50, 3000),
                "מחשבים": (100, 5000),
                "בית וגן": (30, 2000),
                "ספורט ובריאות": (20, 500),
                "אופנה": (30, 800),
                "ילדים ותינוקות": (15, 400),
                "מזון ושתייה": (5, 150),
                "טיפוח ויופי": (10, 300)
            }

            price_range = price_ranges.get(category_name, (10, 500))
            base_price = round(random.uniform(price_range[0], price_range[1]), 2)

            # Generate description with English keywords for search
            descriptions = [
                f"{name} - איכות מעולה ועיצוב מודרני. {search_keywords}",
                f"מוצר איכותי מבית {brand}. {search_keywords}",
                f"{product_name_he} מתקדם עם תכונות חדשניות. {search_keywords}",
                f"הבחירה המושלמת עבור {product_name_he}. {search_keywords}",
                f"{brand} {product_name_he} - המוצר הנמכר ביותר. {search_keywords}",
            ]
            description = random.choice(descriptions)

            # Image URL - using multiple services for real product images
            image_keywords = {
                "אלקטרוניקה": "electronics",
                "מחשבים": "computer",
                "בית וגן": "home",
                "ספורט ובריאות": "fitness",
                "אופנה": "fashion",
                "ילדים ותינוקות": "baby",
                "מזון ושתייה": "food",
                "טיפוח ויופי": "beauty"
            }
            keyword = image_keywords.get(category_name, "product")

            # Use LoremFlickr - provides real photos based on keywords
            image_url = f"https://loremflickr.com/400/300/{keyword}?lock={product_id}"

            products.append({
                "id": product_id,
                "name": name,
                "description": description,
                "category": category_name,
                "image_url": image_url,
                "base_price": base_price,
                "brand": brand,
                "keywords": search_keywords  # Add keywords for better search
            })

            product_id += 1

    return products

# Generate the database
PRODUCTS_DATABASE = generate_products_database(3000)

def get_all_products():
    """Get all products"""
    return PRODUCTS_DATABASE

def get_products_by_category(category: str, limit: int = None):
    """Get products filtered by category"""
    filtered = [p for p in PRODUCTS_DATABASE if p["category"] == category]
    if limit:
        return filtered[:limit]
    return filtered

def search_products(query: str, category: str = None):
    """Search products by name, description, brand, keywords, or category (supports English and Hebrew)"""
    query_lower = query.lower()
    results = []

    for product in PRODUCTS_DATABASE:
        # Category filter
        if category and product["category"] != category:
            continue

        # Text search - search in name, description, brand, keywords, AND category
        if (query_lower in product["name"].lower() or
            query_lower in product["description"].lower() or
            query_lower in product.get("brand", "").lower() or
            query_lower in product.get("keywords", "").lower() or
            query_lower in product.get("category", "").lower()):
            results.append(product)

    return results

def get_categories():
    """Get list of all categories"""
    return list(CATEGORIES.keys())

def get_category_stats():
    """Get statistics about products per category"""
    stats = {}
    for category in get_categories():
        count = len(get_products_by_category(category))
        stats[category] = count
    return stats
