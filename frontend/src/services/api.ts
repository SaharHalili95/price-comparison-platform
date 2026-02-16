import { SearchResponse } from '../types/product';
import { mockProducts, refreshPrices } from '../data/mockProducts';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Simulate API delay for local fallback
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Store refreshed prices in memory (for local fallback)
let currentProducts = [...mockProducts];

/**
 * Search products - tries backend API first, falls back to local mock data.
 */
export const searchProducts = async (query: string, useRefreshed: boolean = false): Promise<SearchResponse> => {
  // Try backend API first
  try {
    const url = new URL(`${API_BASE_URL}/api/products/search`);
    url.searchParams.set('query', query);

    const response = await fetch(url.toString(), {
      signal: AbortSignal.timeout(5000),
    });

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
  // Try backend API
  try {
    const response = await fetch(`${API_BASE_URL}/api/products?limit=50`, {
      signal: AbortSignal.timeout(5000),
    });

    if (response.ok) return;
  } catch {
    // Backend unavailable
  }

  // Fallback: local price refresh
  await delay(800);
  currentProducts = refreshPrices();
};
