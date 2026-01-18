import axios from 'axios';
import { ProductWithPrices, SearchResponse, PriceInfo } from '../types/product';

const API_BASE_URL = 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchProducts = async (query: string): Promise<SearchResponse> => {
  const response = await api.get<SearchResponse>('/products/search', {
    params: { query }
  });
  return response.data;
};

export const getProduct = async (productId: number): Promise<ProductWithPrices> => {
  const response = await api.get<ProductWithPrices>(`/products/${productId}`);
  return response.data;
};

export const getProductPrices = async (productId: number): Promise<PriceInfo[]> => {
  const response = await api.get<PriceInfo[]>(`/products/${productId}/prices`);
  return response.data;
};

export const listProducts = async (category?: string, limit: number = 10): Promise<ProductWithPrices[]> => {
  const response = await api.get<ProductWithPrices[]>('/products', {
    params: { category, limit }
  });
  return response.data;
};

export default api;
