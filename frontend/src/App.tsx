import { NavLink, Route, Routes } from 'react-router-dom'
import { accountsEnabled } from './data/account'
import { isDemo } from './data/api'
import { useBasket } from './data/basket'
import AlertsPage from './pages/AlertsPage'
import BasketPage from './pages/BasketPage'
import ItemPage from './pages/ItemPage'
import SearchPage from './pages/SearchPage'
import StatusPage from './pages/StatusPage'

const link = ({ isActive }: { isActive: boolean }) => `px-3 py-2 rounded-lg ${isActive ? 'bg-blue-700 text-white' : 'text-slate-700'}`

export default function App() {
  const basket = useBasket()
  return (
    <div className="min-h-screen bg-white text-slate-900">
      <header className="border-b border-slate-200">
        <nav className="mx-auto flex max-w-3xl items-center gap-1 px-4 py-3">
          <strong className="me-auto text-lg text-blue-800">SalSmart</strong>
          <NavLink to="/" end className={link}>חיפוש</NavLink>
          <NavLink to="/basket" className={link}>סל ({basket.lines.length})</NavLink>
          {accountsEnabled && <NavLink to="/alerts" className={link}>התראות</NavLink>}
          <NavLink to="/status" className={link}>סטטוס</NavLink>
        </nav>
      </header>
      {isDemo && (
        <p className="bg-amber-50 px-4 py-2 text-center text-sm text-amber-900">
          גרסת דמו: מדגם אמיתי של כמה מאות מוצרים מ-5 סניפים לכל רשת, שנשמר מקבצי המחירים הרשמיים.
        </p>
      )}
      <main className="mx-auto max-w-3xl px-4 py-6">
        <Routes>
          <Route path="/" element={<SearchPage />} />
          <Route path="/item/:barcode" element={<ItemPage />} />
          <Route path="/basket" element={<BasketPage />} />
          <Route path="/status" element={<StatusPage />} />
          {accountsEnabled && <Route path="/alerts" element={<AlertsPage />} />}
        </Routes>
      </main>
    </div>
  )
}
