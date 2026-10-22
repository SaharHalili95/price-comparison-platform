export interface SearchHit {
  barcode: string
  name: string
  manufacturer: string
  min_price: number
  max_price: number
  store_count: number
}

export interface StorePrice {
  chain: string
  store: string
  city: string
  price: number
  unit_price: number | null
  price_updated_at: string | null
}

export interface ItemDetail {
  barcode: string
  name: string
  manufacturer: string
  unit_of_measure: string
  prices: StorePrice[]
}

export interface BasketStore {
  chain: string
  store: string
  city: string
  total: number
  found: number
  missing: string[]
}

export interface ChainStatus {
  chain: string
  status: 'running' | 'success' | 'partial' | 'stale' | 'failed'
  started_at: string
  finished_at: string | null
  newest_file_at: string | null
  files_ok: number
  files_failed: number
  items: number
  price_changes: number
}

export interface PricesApi {
  search(query: string): Promise<SearchHit[]>
  item(barcode: string): Promise<ItemDetail | null>
  compareBasket(barcodes: string[], city?: string): Promise<BasketStore[]>
  cities(): Promise<string[]>
  status(): Promise<ChainStatus[]>
}
