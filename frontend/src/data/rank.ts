import type { BasketStore, ItemDetail, SearchHit } from './types'

// The same rules as the API (backend/app/api/routes.py), for the static demo that has no server.

export function searchItems(items: ItemDetail[], query: string, limit = 20): SearchHit[] {
  const q = query.trim()
  const hits = items
    .filter((i) => i.prices.length && (i.barcode === q || i.name.includes(q)))
    .map((i) => ({
      barcode: i.barcode,
      name: i.name,
      manufacturer: i.manufacturer,
      min_price: Math.min(...i.prices.map((p) => p.price)),
      max_price: Math.max(...i.prices.map((p) => p.price)),
      store_count: i.prices.length,
    }))
  return hits
    .sort((a, b) => Number(b.barcode === q) - Number(a.barcode === q) || b.store_count - a.store_count)
    .slice(0, limit)
}

/** Most complete basket first, then the cheapest total; each store lists what it is missing. */
export function compareBasket(items: ItemDetail[], barcodes: string[], city?: string): BasketStore[] {
  const wanted = [...new Set(barcodes)]
  const stores = new Map<string, BasketStore & { has: Set<string> }>()
  for (const item of items.filter((i) => wanted.includes(i.barcode))) {
    for (const p of item.prices) {
      if (city && p.city !== city) continue
      const key = `${p.chain}|${p.store}`
      const store = stores.get(key) ?? { chain: p.chain, store: p.store, city: p.city, total: 0, found: 0, missing: [], has: new Set() }
      store.total = Math.round((store.total + p.price) * 100) / 100
      store.has.add(item.barcode)
      stores.set(key, store)
    }
  }
  return [...stores.values()]
    .map(({ has, ...s }) => ({ ...s, found: has.size, missing: wanted.filter((b) => !has.has(b)) }))
    .sort((a, b) => b.found - a.found || a.total - b.total)
    .slice(0, 30)
}
