import { useEffect, useState } from 'react'
import { api, isDemo } from '../data/api'
import type { ChainStatus } from '../data/types'
import { date } from '../format'

const LABELS: Record<ChainStatus['status'], string> = {
  success: 'עודכן', partial: 'חלקי', stale: 'נתונים ישנים', failed: 'נכשל', running: 'רץ עכשיו',
}
const COLORS: Record<ChainStatus['status'], string> = {
  success: 'bg-green-100 text-green-800', partial: 'bg-amber-100 text-amber-800', stale: 'bg-amber-100 text-amber-800',
  failed: 'bg-red-100 text-red-800', running: 'bg-blue-100 text-blue-800',
}

export default function StatusPage() {
  const [rows, setRows] = useState<ChainStatus[] | null>(null)
  useEffect(() => {
    api.status().then(setRows).catch(() => setRows([]))
  }, [])
  return (
    <section>
      <h1 className="text-2xl font-bold">סטטוס עדכון</h1>
      <p className="text-slate-600">העדכון האחרון של כל רשת. רשת שנכשלה מוצגת ככזו, עם התאריך האחרון שלה.</p>
      {isDemo && (
        <p className="mt-2 text-sm text-slate-600">
          בדמו מוצגים המספרים של ריצת הטעינה המלאה האחרונה. החיפוש והסל מבוססים על מדגם קטן ממנה.
        </p>
      )}
      <ul className="mt-4 space-y-2">
        {rows?.map((r) => (
          <li key={r.chain} className="rounded-lg border border-slate-200 p-3">
            <div className="flex items-center justify-between">
              <strong>{r.chain}</strong>
              <span className={`rounded-full px-2 py-0.5 text-sm ${COLORS[r.status]}`}>{LABELS[r.status]}</span>
            </div>
            <div className="text-sm text-slate-600">
              עודכן: {date(r.finished_at ?? r.started_at)} · {r.items.toLocaleString('he-IL')} מחירים · {r.files_ok} קבצים
              {r.files_failed > 0 && ` · ${r.files_failed} נכשלו`} · קובץ אחרון: {r.newest_file_at ? date(r.newest_file_at) : 'אין'}
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
