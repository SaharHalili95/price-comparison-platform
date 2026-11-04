import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../data/api'
import { useBasket } from '../data/basket'
import type { SearchHit } from '../data/types'
import { shekel } from '../format'

const EXAMPLES = ['חלב', 'במבה', 'קוטג', 'שוקולד']

const STEPS = [
  { title: 'מחפשים מוצר', text: 'לפי שם או ברקוד, ורואים את טווח המחירים בכל הסניפים.' },
  { title: 'בונים סל', text: 'מוסיפים את המוצרים שאתם קונים בכל שבוע.' },
  { title: 'משווים בעיר שלכם', text: 'רואים כמה הסל השלם עולה בכל חנות, מהזולה ליקרה.' },
]

// Measured in one real ingestion run; see the README.
const FACTS = [
  { value: '1.6M', label: 'מחירים בהרצה אחת, מ-174 חנויות של 3 רשתות' },
  { value: '~1MB', label: 'זיכרון לקובץ XML של 34MB, בפענוח בזרימה' },
  { value: 'K8s', label: 'CronJob לכל רשת, נבדק על אשכול kind ב-CI' },
  { value: 'Alerts', label: 'התראות ירידת מחיר דרך RabbitMQ, עם Prometheus ו-Grafana' },
]

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
      <h1 className="text-3xl font-extrabold leading-tight tracking-tight sm:text-4xl">כמה עולה הסל שלכם בכל סופר?</h1>
      <p className="mt-2 text-lg text-slate-600">
        SalSmart משווה מחירים מקבצי שקיפות המחירים שרשתות השיווק חייבות לפרסם כל יום: מוצר מול מוצר, וסל שלם מול כל החנויות בעיר שלכם.
      </p>
      <input
        className="mt-4 w-full rounded-lg border border-slate-300 px-4 py-3 text-base focus:border-blue-600 focus:outline-none"
        placeholder="שם מוצר או ברקוד"
        aria-label="חיפוש מוצר"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      {!hits && (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="text-sm text-slate-500">נסו:</span>
          {EXAMPLES.map((e) => (
            <button
              key={e}
              className="min-h-9 rounded-full bg-blue-50 px-4 py-1.5 text-sm font-medium text-blue-800 hover:bg-blue-100 active:scale-95"
              onClick={() => setQuery(e)}
            >
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
      {!hits && (
        <>
          <ol className="mt-10 grid gap-6 sm:grid-cols-3">
            {STEPS.map((step, i) => (
              <li key={step.title} className="border-t-2 border-blue-700 pt-3">
                <span className="text-2xl font-extrabold text-blue-700">{i + 1}</span>
                <h2 className="mt-1 font-bold">{step.title}</h2>
                <p className="text-sm text-slate-600">{step.text}</p>
              </li>
            ))}
          </ol>
          <h2 className="mt-12 text-xl font-bold">מתחת למכסה</h2>
          <dl className="mt-4 grid grid-cols-2 gap-x-6 gap-y-5 sm:grid-cols-4">
            {FACTS.map((f) => (
              <div key={f.value} className="border-t border-slate-200 pt-3">
                <dt className="text-2xl font-extrabold text-blue-800" dir="ltr">{f.value}</dt>
                <dd className="mt-1 text-sm text-slate-600">{f.label}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-8 text-sm text-slate-600" dir="ltr" lang="en">
            In English: SalSmart ingests the daily price files Israeli supermarket chains must publish (1.6M prices per run), normalizes their XML formats into PostgreSQL, and compares a full basket across the stores in your city. Python, FastAPI, PostgreSQL, React, Kubernetes, RabbitMQ.{' '}
            <a className="text-blue-700 underline" href="https://github.com/SaharHalili95/price-comparison-platform" target="_blank" rel="noopener noreferrer">
              Source on GitHub
            </a>
          </p>
        </>
      )}
    </section>
  )
}
