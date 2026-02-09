export enum SourceEnum {
  KSP = "KSP",
  BUG = "Bug",
  ZAP = "Zap"
}

export interface PriceInfo {
  source: SourceEnum;
  price: number;
  currency: string;
  availability: boolean;
  url?: string;
  last_updated: string;
}

export interface Product {
  id: number;
  name: string;
  description?: string;
  category?: string;
  image_url?: string;
  created_at: string;
  updated_at?: string;
}

export interface ProductWithPrices extends Product {
  prices: PriceInfo[];
  lowest_price?: number;
  highest_price?: number;
  average_price?: number;
}

export interface SearchResponse {
  query: string;
  total_results: number;
  products: ProductWithPrices[];
}
