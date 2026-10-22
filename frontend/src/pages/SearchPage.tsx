import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../data/api'
import { useBasket } from '../data/basket'
import type { SearchHit } from '../data/types'
import { shekel } from '../format'

const EXAMPLES = ['חלב', 'במבה', 'קוטג', 'שוקולד']

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [hits, setHits] = useState<SearchHit[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const basket = useBasket()

  useEffect(() => {
    if (query.trim().length < 2) {
      setHits(null)
      return
    }
    let current = true
    const timer = setTimeout(() => {
      api.search(query)
        .then((h) => current && (setHits(h), setError(null)))
        .catch((e: Error) => current && setError(e.message))
    }, 250)
    return () => {
      current = false
      clearTimeout(timer)
    }
  }, [query])

  return (
    <section>
      <h1 className="text-2xl font-bold">חיפוש מוצר</h1>
      <p className="text-slate-600 mt-1">מחירים מקבצי שקיפות המחירים הרשמיים של רשתות השיווק.</p>
      <input
        className="mt-4 w-full rounded-lg border border-slate-300 px-4 py-3 text-base focus:border-blue-600 focus:outline-none"
        placeholder="שם מוצר או ברקוד"
        aria-label="חיפוש מוצר"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      {!hits && (
        <div className="mt-3 flex flex-wrap gap-2">
          {EXAMPLES.map((e) => (
            <button key={e} className="rounded-full bg-slate-100 px-3 py-1 text-sm" onClick={() => setQuery(e)}>
              {e}
            </button>
          ))}
        </div>
      )}
      {error && <p className="mt-4 text-red-700">שגיאה: {error}</p>}
      {hits && hits.length === 0 && <p className="mt-4 text-slate-600">לא נמצאו מוצרים.</p>}
      <ul className="mt-4 divide-y divide-slate-200">
        {hits?.map((h) => (
          <li key={h.barcode} className="flex items-center justify-between gap-3 py-3">
            <Link to={`/item/${encodeURIComponent(h.barcode)}`} className="min-w-0">
              <div className="font-medium truncate">{h.name}</div>
              <div className="text-sm text-slate-500">
                {h.manufacturer} · {h.store_count} סניפים · {shekel(h.min_price)}
                {h.max_price > h.min_price && ` עד ${shekel(h.max_price)}`}
              </div>
            </Link>
            <button
              className="shrink-0 rounded-lg border border-blue-600 px-3 py-2 text-sm text-blue-700 disabled:opacity-50"
              disabled={basket.has(h.barcode)}
              onClick={() => basket.add({ barcode: h.barcode, name: h.name })}
            >
              {basket.has(h.barcode) ? 'בסל' : 'הוסף לסל'}
            </button>
          </li>
        ))}
      </ul>
    </section>
  )
}
