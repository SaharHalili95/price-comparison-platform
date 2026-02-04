import { ProductWithPrices, SearchResponse, PriceInfo } from '../types/product';
import { mockProducts, refreshPrices } from '../data/mockProducts';

// Simulate API delay for realistic feel
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Store refreshed prices in memory
let currentProducts = [...mockProducts];

export const searchProducts = async (query: string, useRefreshed: boolean = false): Promise<SearchResponse> => {
  await delay(300); // Simulate network delay

  // Use refreshed prices if requested
  const dataSource = useRefreshed ? currentProducts : mockProducts;

  // Apply search filter
  const products = query && query.trim()
    ? dataSource.filter(product =>
        product.name.toLowerCase().includes(query.toLowerCase()) ||
        product.description?.toLowerCase().includes(query.toLowerCase()) ||
        product.category?.toLowerCase().includes(query.toLowerCase())
      )
    : dataSource;

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

  let products = [...currentProducts];

  if (category) {
    products = products.filter(p => p.category === category);
  }

  return products.slice(0, limit);
};

// Refresh all prices with new data
export const refreshAllPrices = async (): Promise<void> => {
  await delay(800); // Simulate longer API call for price refresh
  currentProducts = refreshPrices();
};
