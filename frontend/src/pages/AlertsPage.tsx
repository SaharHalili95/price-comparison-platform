import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { deleteAlert, getToken, googleClientId, listAlerts, signInWithGoogle, signOut, type Alert } from '../data/account'
import { shekel } from '../format'

declare global {
  interface Window {
    google?: { accounts: { id: { initialize(o: object): void; renderButton(el: HTMLElement, o: object): void } } }
  }
}

function GoogleButton({ onSignedIn }: { onSignedIn: () => void }) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.onload = () => {
      window.google?.accounts.id.initialize({
        client_id: googleClientId,
        callback: ({ credential }: { credential: string }) => signInWithGoogle(credential).then(onSignedIn),
      })
      if (ref.current) window.google?.accounts.id.renderButton(ref.current, { locale: 'he', text: 'signin_with' })
    }
    document.head.appendChild(script)
    return () => script.remove()
  }, [onSignedIn])
  return <div ref={ref} />
}

export default function AlertsPage() {
  const [signedIn, setSignedIn] = useState(Boolean(getToken()))
  const [alerts, setAlerts] = useState<Alert[]>([])

  useEffect(() => {
    if (signedIn) listAlerts().then(setAlerts).catch(() => setSignedIn(Boolean(getToken())))
  }, [signedIn])

  if (!signedIn) {
    return (
      <section>
        <h1 className="text-2xl font-bold">התראות מחיר</h1>
        <p className="my-3 text-slate-600">התחברו כדי לקבל מייל כשמחיר של מוצר יורד.</p>
        <GoogleButton onSignedIn={() => setSignedIn(true)} />
      </section>
    )
  }
  return (
    <section>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">התראות מחיר</h1>
        <button className="text-sm text-slate-600 underline" onClick={() => (signOut(), setSignedIn(false))}>התנתקות</button>
      </div>
      {alerts.length === 0 && <p className="mt-3 text-slate-600">אין התראות. בדף של מוצר אפשר ללחוץ "התראה על ירידת מחיר".</p>}
      <ul className="mt-3 divide-y divide-slate-200">
        {alerts.map((a) => (
          <li key={a.id} className="flex items-center justify-between gap-2 py-3">
            <Link to={`/item/${encodeURIComponent(a.barcode)}`}>
              <div className="font-medium">{a.name}</div>
              <div className="text-sm text-slate-500">
                {a.target_price ? `כשהמחיר יגיע ל-${shekel(a.target_price)}` : 'בכל ירידת מחיר'}
                {a.current_min_price !== null && ` · היום מ-${shekel(a.current_min_price)}`}
              </div>
            </Link>
            <button aria-label={`מחק התראה ${a.name}`} onClick={() => deleteAlert(a.id).then(() => setAlerts((x) => x.filter((y) => y.id !== a.id)))}>✕</button>
          </li>
        ))}
      </ul>
    </section>
  )
}
