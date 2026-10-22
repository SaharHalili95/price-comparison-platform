import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../data/api'
import { useBasket } from '../data/basket'
import type { ItemDetail } from '../data/types'
import { date, shekel } from '../format'

export default function ItemPage() {
  const { barcode = '' } = useParams()
  const [item, setItem] = useState<ItemDetail | null | undefined>(undefined)
  const basket = useBasket()

  useEffect(() => {
    api.item(barcode).then(setItem).catch(() => setItem(null))
  }, [barcode])

  if (item === undefined) return <p>טוען...</p>
  if (item === null) return <p>המוצר לא נמצא.</p>
  const cheapest = item.prices[0]?.price

  return (
    <section>
      <h1 className="text-2xl font-bold">{item.name}</h1>
      <p className="text-slate-600">{item.manufacturer} · ברקוד <span dir="ltr">{item.barcode}</span></p>
      <button
        className="mt-3 rounded-lg bg-blue-700 px-4 py-2 text-white disabled:opacity-50"
        disabled={basket.has(item.barcode)}
        onClick={() => basket.add({ barcode: item.barcode, name: item.name })}
      >
        {basket.has(item.barcode) ? 'בסל' : 'הוסף לסל'}
      </button>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[480px] text-right">
          <thead className="text-sm text-slate-500">
            <tr><th className="py-2">רשת</th><th>סניף</th><th>עיר</th><th>מחיר</th><th>עודכן</th></tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {item.prices.map((p) => (
              <tr key={`${p.chain}-${p.store}`} className={p.price === cheapest ? 'bg-green-50' : ''}>
                <td className="py-2">{p.chain}</td>
                <td>{p.store}</td>
                <td>{p.city || '-'}</td>
                <td className="font-semibold">{shekel(p.price)}</td>
                <td className="text-sm text-slate-500">{p.price_updated_at ? date(p.price_updated_at) : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
