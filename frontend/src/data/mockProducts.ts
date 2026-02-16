import { ProductWithPrices } from '../types/product';
import { generateProducts } from './productGenerator';
import { electronicsProducts, computersProducts } from './templates/electronics';
import { fashionProducts, homeGardenProducts } from './templates/fashion';
import { sportsProducts, kidsProducts } from './templates/lifestyle';
import { foodProducts, beautyProducts } from './templates/food-beauty';

// Generate all products with unique IDs (spaced by 200 to avoid collisions)
const electronics = generateProducts(electronicsProducts, 'אלקטרוניקה', 1);
const computers = generateProducts(computersProducts, 'מחשבים', 201);
const fashion = generateProducts(fashionProducts, 'אופנה', 401);
const homeGarden = generateProducts(homeGardenProducts, 'בית וגן', 601);
const sports = generateProducts(sportsProducts, 'ספורט ובריאות', 801);
const kids = generateProducts(kidsProducts, 'ילדים ותינוקות', 1001);
const food = generateProducts(foodProducts, 'מזון ושתייה', 1201);
const beauty = generateProducts(beautyProducts, 'טיפוח ויופי', 1401);

export const mockProducts: ProductWithPrices[] = [
  ...electronics,
  ...computers,
  ...fashion,
  ...homeGarden,
  ...sports,
  ...kids,
  ...food,
  ...beauty,
];

// Refresh prices with random variations (simulates real-time price updates)
export const refreshPrices = (): ProductWithPrices[] => {
  const now = new Date().toISOString().split('T')[0];

  return mockProducts.map(product => {
    const updatedPrices = product.prices.map(priceInfo => {
      // Randomly adjust price by -5% to +5%
      const variation = (Math.random() * 0.1 - 0.05);
      const newPrice = Math.round(priceInfo.price * (1 + variation));

      // Randomly toggle availability (90% chance to be available)
      const newAvailability = Math.random() > 0.1;

      return {
        ...priceInfo,
        price: newPrice,
        availability: newAvailability,
        last_updated: now,
      };
    });

    // Recalculate price statistics
    const availablePrices = updatedPrices
      .filter(p => p.availability)
      .map(p => p.price);

    const lowest = availablePrices.length > 0
      ? Math.min(...availablePrices)
      : undefined;
    const highest = availablePrices.length > 0
      ? Math.max(...availablePrices)
      : undefined;
    const average = availablePrices.length > 0
      ? Math.round(availablePrices.reduce((a, b) => a + b, 0) / availablePrices.length)
      : undefined;

    return {
      ...product,
      prices: updatedPrices,
      lowest_price: lowest,
      highest_price: highest,
      average_price: average,
    };
  });
};
