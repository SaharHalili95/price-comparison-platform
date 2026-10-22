import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../data/api'
import { useBasket } from '../data/basket'
import type { BasketStore } from '../data/types'
import { shekel } from '../format'

export default function BasketPage() {
  const basket = useBasket()
  const [city, setCity] = useState('')
  const [cities, setCities] = useState<string[]>([])
  const [stores, setStores] = useState<BasketStore[] | null>(null)
  const barcodes = basket.lines.map((l) => l.barcode)
  const names = Object.fromEntries(basket.lines.map((l) => [l.barcode, l.name]))

  useEffect(() => {
    api.cities().then(setCities).catch(() => setCities([]))
  }, [])

  useEffect(() => {
    if (!barcodes.length) {
      setStores(null)
      return
    }
    api.compareBasket(barcodes, city || undefined).then(setStores).catch(() => setStores([]))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [barcodes.join(','), city])

  if (!basket.lines.length) {
    return (
      <section>
        <h1 className="text-2xl font-bold">הסל שלי</h1>
        <p className="mt-2 text-slate-600">הסל ריק. <Link to="/" className="text-blue-700 underline">חפשו מוצרים</Link> והוסיפו אותם.</p>
      </section>
    )
  }

  return (
    <section>
      <h1 className="text-2xl font-bold">הסל שלי</h1>
      <ul className="mt-3 flex flex-wrap gap-2">
        {basket.lines.map((l) => (
          <li key={l.barcode} className="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-sm">
            {l.name}
            <button aria-label={`הסר ${l.name}`} onClick={() => basket.remove(l.barcode)}>✕</button>
          </li>
        ))}
      </ul>
      <label className="mt-4 block text-sm text-slate-600">
        עיר
        <select className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-base" value={city} onChange={(e) => setCity(e.target.value)}>
          <option value="">כל הערים</option>
          {cities.map((c) => <option key={c}>{c}</option>)}
        </select>
      </label>
      {stores && stores.length === 0 && <p className="mt-4 text-slate-600">אין סניף עם המוצרים האלה בעיר הזו.</p>}
      <ol className="mt-4 space-y-2">
        {stores?.map((s, index) => (
          <li key={`${s.chain}-${s.store}`} className={`rounded-lg border p-3 ${index === 0 ? 'border-green-600 bg-green-50' : 'border-slate-200'}`}>
            <div className="flex justify-between gap-2">
              <strong>{s.chain} · {s.store}</strong>
              <strong>{shekel(s.total)}</strong>
            </div>
            <div className="text-sm text-slate-600">
              {s.city || 'עיר לא ידועה'} · {s.found} מתוך {barcodes.length} מוצרים
              {s.missing.length > 0 && ` · חסר: ${s.missing.map((b) => names[b] ?? b).join(', ')}`}
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}
