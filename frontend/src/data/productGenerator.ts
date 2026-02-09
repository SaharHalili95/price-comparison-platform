import { ProductWithPrices, SourceEnum } from '../types/product';

// Category colors for product placeholder images [background, text]
const categoryColors: Record<string, [string, string]> = {
  'אלקטרוניקה': ['1a365d', 'e2e8f0'],
  'מחשבים': ['2d1b69', 'e9d5ff'],
  'אופנה': ['831843', 'fce7f3'],
  'בית וגן': ['14532d', 'd1fae5'],
  'ספורט ובריאות': ['7c2d12', 'fed7aa'],
  'ילדים ותינוקות': ['581c87', 'f3e8ff'],
  'מזון ושתייה': ['7f1d1d', 'fecaca'],
  'טיפוח ויופי': ['4a1942', 'fae8ff'],
};

function getImage(productName: string, category: string): string {
  const [bg, fg] = categoryColors[category] || ['374151', 'e5e7eb'];
  const text = encodeURIComponent(productName.slice(0, 40));
  return `https://placehold.co/400x300/${bg}/${fg}?text=${text}`;
}

// Seeded random for consistent prices
function seededRandom(seed: number): number {
  const x = Math.sin(seed * 9301 + 49297) * 49297;
  return x - Math.floor(x);
}

export function generateProducts(
  templates: [string, string, number][],
  category: string,
  startId: number
): ProductWithPrices[] {
  return templates.map((t, i) => {
    const [name, description, basePrice] = t;
    const id = startId + i;
    const seed = id * 7;

    const kspVar = 1 + (seededRandom(seed) * 0.1 - 0.02);
    const bugVar = 1 + (seededRandom(seed + 1) * 0.1 - 0.08);
    const zapVar = 1 + (seededRandom(seed + 2) * 0.1 + 0.01);

    const kspPrice = Math.round(basePrice * kspVar);
    const bugPrice = Math.round(basePrice * bugVar);
    const zapPrice = Math.round(basePrice * zapVar);

    const kspAvail = seededRandom(seed + 3) > 0.1;
    const bugAvail = seededRandom(seed + 4) > 0.15;
    const zapAvail = seededRandom(seed + 5) > 0.2;

    const prices = [
      { source: SourceEnum.KSP, price: kspPrice, currency: '₪', availability: kspAvail, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.BUG, price: bugPrice, currency: '₪', availability: bugAvail, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.ZAP, price: zapPrice, currency: '₪', availability: zapAvail, url: '#', last_updated: '2024-02-04' },
    ];

    const availPrices = prices.filter(p => p.availability).map(p => p.price);
    const lowest = availPrices.length > 0 ? Math.min(...availPrices) : undefined;
    const highest = availPrices.length > 0 ? Math.max(...availPrices) : undefined;
    const average = availPrices.length > 0 ? Math.round(availPrices.reduce((a, b) => a + b, 0) / availPrices.length) : undefined;

    const day = String((i % 28) + 1).padStart(2, '0');

    return {
      id,
      name,
      description,
      category,
      image_url: getImage(name, category),
      created_at: `2024-01-${day}`,
      prices,
      lowest_price: lowest,
      highest_price: highest,
      average_price: average,
    };
  });
}
