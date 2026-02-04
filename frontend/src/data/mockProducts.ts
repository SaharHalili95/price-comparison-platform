import { ProductWithPrices, SourceEnum } from '../types/product';

// Hebrew Product Database with Real-like Israeli Products
export const mockProducts: ProductWithPrices[] = [
  // Electronics
  {
    id: 1,
    name: 'iPhone 15 Pro Max 256GB',
    description: 'iPhone 15 Pro Max עם מסך 6.7 אינץ׳, שבב A17 Pro, מצלמה טיטניום',
    category: 'אלקטרוניקה',
    image_url: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400',
    created_at: '2024-01-15',
    prices: [
      { source: SourceEnum.AMAZON, price: 5299, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.EBAY, price: 4999, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.WALMART, price: 5399, currency: '₪', availability: false, url: '#', last_updated: '2024-02-04' },
    ],
    lowest_price: 4999,
    highest_price: 5399,
    average_price: 5232,
  },
  {
    id: 2,
    name: 'Samsung Galaxy S24 Ultra 512GB',
    description: 'Galaxy S24 Ultra עם מסך 6.8 אינץ׳, Snapdragon 8 Gen 3, עט S Pen',
    category: 'אלקטרוניקה',
    image_url: 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400',
    created_at: '2024-01-20',
    prices: [
      { source: SourceEnum.AMAZON, price: 4799, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.EBAY, price: 4599, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.WALMART, price: 4899, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
    ],
    lowest_price: 4599,
    highest_price: 4899,
    average_price: 4766,
  },
  {
    id: 3,
    name: 'MacBook Air M3 15" 16GB 512GB',
    description: 'MacBook Air עם שבב M3, מסך Liquid Retina 15.3 אינץ׳',
    category: 'מחשבים',
    image_url: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400',
    created_at: '2024-01-10',
    prices: [
      { source: SourceEnum.AMAZON, price: 6299, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.EBAY, price: 5999, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.WALMART, price: 6499, currency: '₪', availability: false, url: '#', last_updated: '2024-02-04' },
    ],
    lowest_price: 5999,
    highest_price: 6499,
    average_price: 6266,
  },
  {
    id: 4,
    name: 'Sony WH-1000XM5 אוזניות אלחוטיות',
    description: 'אוזניות עם ביטול רעשים מתקדם, איכות שמע פרימיום, 30 שעות סוללה',
    category: 'אוזניות',
    image_url: 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400',
    created_at: '2024-01-25',
    prices: [
      { source: SourceEnum.AMAZON, price: 1299, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.EBAY, price: 1199, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.WALMART, price: 1349, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
    ],
    lowest_price: 1199,
    highest_price: 1349,
    average_price: 1282,
  },
  {
    id: 5,
    name: 'iPad Pro 12.9" M2 256GB WiFi',
    description: 'iPad Pro עם שבב M2, מסך Liquid Retina XDR 12.9 אינץ׳',
    category: 'טאבלטים',
    image_url: 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400',
    created_at: '2024-01-12',
    prices: [
      { source: SourceEnum.AMAZON, price: 4599, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.EBAY, price: 4399, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.WALMART, price: 4799, currency: '₪', availability: false, url: '#', last_updated: '2024-02-04' },
    ],
    lowest_price: 4399,
    highest_price: 4799,
    average_price: 4599,
  },

  // Home Appliances
  {
    id: 6,
    name: 'Dyson V15 Detect שואב אבק אלחוטי',
    description: 'שואב אבק אלחוטי עם טכנולוגיית זיהוי לייזר, 60 דקות סוללה',
    category: 'מוצרי חשמל',
    image_url: 'https://images.unsplash.com/photo-1558317374-067fb5f30001?w=400',
    created_at: '2024-01-18',
    prices: [
      { source: SourceEnum.AMAZON, price: 2499, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.EBAY, price: 2299, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.WALMART, price: 2599, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
    ],
    lowest_price: 2299,
    highest_price: 2599,
    average_price: 2466,
  },
  {
    id: 7,
    name: 'Nespresso Vertuo מכונת קפה',
    description: 'מכונת קפה Nespresso עם טכנולוגיית Centrifusion, 5 גדלים',
    category: 'מוצרי חשמל',
    image_url: 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400',
    created_at: '2024-01-22',
    prices: [
      { source: SourceEnum.AMAZON, price: 799, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.EBAY, price: 749, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.WALMART, price: 849, currency: '₪', availability: false, url: '#', last_updated: '2024-02-04' },
    ],
    lowest_price: 749,
    highest_price: 849,
    average_price: 799,
  },
  {
    id: 8,
    name: 'LG OLED65C3 טלוויזיה 65 אינץ׳',
    description: 'טלוויזיית OLED 4K עם AI, HDR10, Dolby Vision, 120Hz',
    category: 'טלוויזיות',
    image_url: 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400',
    created_at: '2024-01-08',
    prices: [
      { source: SourceEnum.AMAZON, price: 6999, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.EBAY, price: 6599, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.WALMART, price: 7299, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
    ],
    lowest_price: 6599,
    highest_price: 7299,
    average_price: 6966,
  },

  // Gaming
  {
    id: 9,
    name: 'PlayStation 5 Slim 1TB',
    description: 'קונסולת PS5 Slim עם דיסק, 1TB, כולל DualSense Controller',
    category: 'גיימינג',
    image_url: 'https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400',
    created_at: '2024-01-30',
    prices: [
      { source: SourceEnum.AMAZON, price: 2299, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.EBAY, price: 2199, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.WALMART, price: 2399, currency: '₪', availability: false, url: '#', last_updated: '2024-02-04' },
    ],
    lowest_price: 2199,
    highest_price: 2399,
    average_price: 2299,
  },
  {
    id: 10,
    name: 'Nintendo Switch OLED',
    description: 'Nintendo Switch OLED עם מסך 7 אינץ׳, 64GB',
    category: 'גיימינג',
    image_url: 'https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=400',
    created_at: '2024-01-28',
    prices: [
      { source: SourceEnum.AMAZON, price: 1499, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.EBAY, price: 1399, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.WALMART, price: 1549, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
    ],
    lowest_price: 1399,
    highest_price: 1549,
    average_price: 1482,
  },

  // Smart Home
  {
    id: 11,
    name: 'Amazon Echo Dot 5th Gen',
    description: 'רמקול חכם עם Alexa, איכות שמע משופרת',
    category: 'בית חכם',
    image_url: 'https://images.unsplash.com/photo-1543512214-318c7553f230?w=400',
    created_at: '2024-01-14',
    prices: [
      { source: SourceEnum.AMAZON, price: 249, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.EBAY, price: 229, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.WALMART, price: 269, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
    ],
    lowest_price: 229,
    highest_price: 269,
    average_price: 249,
  },
  {
    id: 12,
    name: 'Philips Hue Starter Kit',
    description: 'ערכת תאורה חכמה עם 3 נורות צבעוניות וגשר',
    category: 'בית חכם',
    image_url: 'https://images.unsplash.com/photo-1558089687-5e5d6c7fb58e?w=400',
    created_at: '2024-01-16',
    prices: [
      { source: SourceEnum.AMAZON, price: 549, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.EBAY, price: 499, currency: '₪', availability: true, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.WALMART, price: 599, currency: '₪', availability: false, url: '#', last_updated: '2024-02-04' },
    ],
    lowest_price: 499,
    highest_price: 599,
    average_price: 549,
  },
];

// Search function for mock data
export const searchMockProducts = (query: string): ProductWithPrices[] => {
  if (!query || query.trim() === '') {
    return mockProducts;
  }

  const searchTerm = query.toLowerCase().trim();

  return mockProducts.filter(product =>
    product.name.toLowerCase().includes(searchTerm) ||
    product.description?.toLowerCase().includes(searchTerm) ||
    product.category?.toLowerCase().includes(searchTerm)
  );
};
