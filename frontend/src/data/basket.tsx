import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

export interface BasketLine {
  barcode: string
  name: string
}

interface Basket {
  lines: BasketLine[]
  has(barcode: string): boolean
  add(line: BasketLine): void
  remove(barcode: string): void
  clear(): void
}

const KEY = 'salsmart.basket'
const BasketContext = createContext<Basket | null>(null)

function read(): BasketLine[] {
  try {
    return JSON.parse(localStorage.getItem(KEY) ?? '[]') as BasketLine[]
  } catch {
    return []
  }
}

/** Kept in the browser until Phase 4 adds saved baskets for signed-in users. */
export function BasketProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<BasketLine[]>(read)
  useEffect(() => {
    try {
      localStorage.setItem(KEY, JSON.stringify(lines))
    } catch {
      // Storage can be blocked; the basket then lasts for this visit.
    }
  }, [lines])
  const basket: Basket = {
    lines,
    has: (barcode) => lines.some((l) => l.barcode === barcode),
    add: (line) => setLines((ls) => (ls.some((l) => l.barcode === line.barcode) ? ls : [...ls, line])),
    remove: (barcode) => setLines((ls) => ls.filter((l) => l.barcode !== barcode)),
    clear: () => setLines([]),
  }
  return <BasketContext.Provider value={basket}>{children}</BasketContext.Provider>
}

export function useBasket(): Basket {
  const basket = useContext(BasketContext)
  if (!basket) throw new Error('useBasket must be used inside BasketProvider')
  return basket
}
