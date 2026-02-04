import { ProductWithPrices, SearchResponse, PriceInfo } from '../types/product';
import { mockProducts, searchMockProducts } from '../data/mockProducts';

// Simulate API delay for realistic feel
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const searchProducts = async (query: string): Promise<SearchResponse> => {
  await delay(300); // Simulate network delay

  const products = searchMockProducts(query);

  return {
    products,
    total_results: products.length,
    query
  };
};

export const getProduct = async (productId: number): Promise<ProductWithPrices> => {
  await delay(200);

  const product = mockProducts.find(p => p.id === productId);

  if (!product) {
    throw new Error(`Product with id ${productId} not found`);
  }

  return product;
};

export const getProductPrices = async (productId: number): Promise<PriceInfo[]> => {
  await delay(200);

  const product = mockProducts.find(p => p.id === productId);

  if (!product) {
    throw new Error(`Product with id ${productId} not found`);
  }

  return product.prices;
};

export const listProducts = async (category?: string, limit: number = 10): Promise<ProductWithPrices[]> => {
  await delay(300);

  let products = [...mockProducts];

  if (category) {
    products = products.filter(p => p.category === category);
  }

  return products.slice(0, limit);
};
