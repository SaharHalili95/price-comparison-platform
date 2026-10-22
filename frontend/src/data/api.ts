import { compareBasket, searchItems } from './rank'
import type { ChainStatus, ItemDetail, PricesApi } from './types'

interface Snapshot {
  items: ItemDetail[]
  cities: string[]
  status: ChainStatus[]
}

const apiUrl = import.meta.env.VITE_API_URL as string | undefined
export const isDemo = !apiUrl

async function json<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...init })
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`)
  return response.json() as Promise<T>
}

function httpApi(base: string): PricesApi {
  return {
    search: async (q) => (await json<{ items: never[] }>(`${base}/items/search?q=${encodeURIComponent(q)}`)).items,
    item: async (barcode) => {
      const response = await fetch(`${base}/items/${encodeURIComponent(barcode)}`)
      return response.status === 404 ? null : ((await response.json()) as ItemDetail)
    },
    compareBasket: async (barcodes, city) =>
      (await json<{ stores: never[] }>(`${base}/basket/compare`, { method: 'POST', body: JSON.stringify({ barcodes, city: city || null }) })).stores,
    cities: () => json(`${base}/cities`),
    status: () => json(`${base}/status`),
  }
}

/** GitHub Pages has no server: a real slice of the database is shipped as JSON and queried in the browser. */
function snapshotApi(): PricesApi {
  let snapshot: Promise<Snapshot> | undefined
  const load = () => (snapshot ??= json<Snapshot>(`${import.meta.env.BASE_URL}demo-snapshot.json`))
  return {
    search: async (q) => searchItems((await load()).items, q),
    item: async (barcode) => (await load()).items.find((i) => i.barcode === barcode) ?? null,
    compareBasket: async (barcodes, city) => compareBasket((await load()).items, barcodes, city),
    cities: async () => (await load()).cities,
    status: async () => (await load()).status,
  }
}

export const api: PricesApi = apiUrl ? httpApi(apiUrl) : snapshotApi()
