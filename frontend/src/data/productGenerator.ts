import { ProductWithPrices, SourceEnum } from '../types/product';

// Unsplash image collections by category
const categoryImages: Record<string, string[]> = {
  'אלקטרוניקה': [
    'photo-1695048133142-1a20484d2569', 'photo-1610945415295-d9bbf067e59c',
    'photo-1511707171634-5f897ff02aa9', 'photo-1574944985070-8f3ebc6b79d2',
    'photo-1605236453806-6ff36851218e', 'photo-1592899677977-9c10ca588bbd',
  ],
  'מחשבים': [
    'photo-1517336714731-489689fd1ca8', 'photo-1496181133206-80ce9b88a853',
    'photo-1588872657578-7efd1f1555ed', 'photo-1525547719571-a2d4ac8945e2',
    'photo-1593642702821-c8da6771f0c6', 'photo-1587614382346-4ec70e388b28',
  ],
  'אופנה': [
    'photo-1441986300917-64674bd600d8', 'photo-1489987707025-afc232f7ea0f',
    'photo-1558171813-4c088753af8f', 'photo-1556905055-8f358a7a47b2',
    'photo-1483985988355-763728e1935b', 'photo-1469334031218-e382a71b716b',
  ],
  'בית וגן': [
    'photo-1556909114-f6e7ad7d3136', 'photo-1558317374-067fb5f30001',
    'photo-1556228453-efd6c1ff04f6', 'photo-1583847268964-b28dc8f51f92',
    'photo-1513694203232-719a280e022f', 'photo-1524758631624-e2822e304c36',
  ],
  'ספורט ובריאות': [
    'photo-1517836357463-d25dfeac3438', 'photo-1576678927484-cc907957088c',
    'photo-1571019614242-c5c5dee9f50b', 'photo-1518611012118-696072aa579a',
    'photo-1526506118085-60ce8714f8c5', 'photo-1590239926044-4131f5d0654d',
  ],
  'ילדים ותינוקות': [
    'photo-1515488042361-ee00e0ddd4e4', 'photo-1596461404969-9ae70f2830c1',
    'photo-1555252333-9f8e92e65df9', 'photo-1587654780013-04759610c472',
    'photo-1566004100477-7b7be4da9116', 'photo-1606092195730-5d7b9af1efc5',
  ],
  'מזון ושתייה': [
    'photo-1546069901-ba9599a7e63c', 'photo-1559056199-641a0ac8b55e',
    'photo-1495474472287-4d71bcdd2085', 'photo-1504674900247-0877df9cc836',
    'photo-1567306226416-28f0efdc88ce', 'photo-1571091718767-18b5b1457add',
  ],
  'טיפוח ויופי': [
    'photo-1596462502278-27bfdc403348', 'photo-1571781926291-c477ebfd024b',
    'photo-1512496015851-a90fb38ba796', 'photo-1522335789203-aabd1fc54bc9',
    'photo-1556228578-0d85b1a4d571', 'photo-1598440947619-2c35fc9aa908',
  ],
};

function getImage(category: string, index: number): string {
  const images = categoryImages[category] || categoryImages['אלקטרוניקה'];
  return `https://images.unsplash.com/${images[index % images.length]}?w=400`;
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

    const amazonVar = 1 + (seededRandom(seed) * 0.1 - 0.02);
    const ebayVar = 1 + (seededRandom(seed + 1) * 0.1 - 0.08);
    const walmartVar = 1 + (seededRandom(seed + 2) * 0.1 + 0.01);

    const amazonPrice = Math.round(basePrice * amazonVar);
    const ebayPrice = Math.round(basePrice * ebayVar);
    const walmartPrice = Math.round(basePrice * walmartVar);

    const amazonAvail = seededRandom(seed + 3) > 0.1;
    const ebayAvail = seededRandom(seed + 4) > 0.15;
    const walmartAvail = seededRandom(seed + 5) > 0.2;

    const prices = [
      { source: SourceEnum.KSP, price: amazonPrice, currency: '₪', availability: amazonAvail, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.BUG, price: ebayPrice, currency: '₪', availability: ebayAvail, url: '#', last_updated: '2024-02-04' },
      { source: SourceEnum.ZAP, price: walmartPrice, currency: '₪', availability: walmartAvail, url: '#', last_updated: '2024-02-04' },
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
      image_url: getImage(category, i),
      created_at: `2024-01-${day}`,
      prices,
      lowest_price: lowest,
      highest_price: highest,
      average_price: average,
    };
  });
}
