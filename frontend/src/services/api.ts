import { SearchResponse } from '../types/product';
import { mockProducts, refreshPrices } from '../data/mockProducts';
import { authFetch } from './authApi';

// Simulate API delay for local fallback
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Store refreshed prices in memory (for local fallback)
let currentProducts = [...mockProducts];

/**
 * Search products - tries backend API first, falls back to local mock data.
 */
export const searchProducts = async (query: string, useRefreshed: boolean = false): Promise<SearchResponse> => {
  try {
    const params = new URLSearchParams({ query });
    const response = await authFetch(`/api/products/search?${params}`);

    if (response.ok) {
      return await response.json();
    }
  } catch {
    // Backend unavailable - fall back to local mock data
  }

  // Fallback: use local mock data
  await delay(300);
  const dataSource = useRefreshed ? currentProducts : mockProducts;

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

/**
 * Refresh all prices - tries backend, falls back to local refresh.
 */
export const refreshAllPrices = async (): Promise<void> => {
  try {
    const response = await authFetch('/api/products?limit=50');
    if (response.ok) return;
  } catch {
    // Backend unavailable
  }

  // Fallback: local price refresh
  await delay(800);
  currentProducts = refreshPrices();
};
