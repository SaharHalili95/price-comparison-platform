import { SearchResponse } from '../types/product';
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

// Refresh all prices with new data
export const refreshAllPrices = async (): Promise<void> => {
  await delay(800); // Simulate longer API call for price refresh
  currentProducts = refreshPrices();
};
