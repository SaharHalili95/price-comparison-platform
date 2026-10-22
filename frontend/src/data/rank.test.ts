import { describe, expect, it } from 'vitest'
import { compareBasket, searchItems } from './rank'
import type { ItemDetail } from './types'

const price = (chain: string, store: string, city: string, p: number) => ({ chain, store, city, price: p, unit_price: null, price_updated_at: null })
const items: ItemDetail[] = [
  { barcode: '7290000000001', name: 'חלב 3% קרטון', manufacturer: 'תנובה', unit_of_measure: 'ליטר', prices: [price('רמי לוי', 'תלפיות', 'ירושלים', 6.2), price('אושר עד', 'מגדל העמק', 'מגדל העמק', 6.9)] },
  { barcode: '7290000000002', name: 'במבה 80 גרם', manufacturer: 'אסם', unit_of_measure: 'גרם', prices: [price('רמי לוי', 'תלפיות', 'ירושלים', 4.5)] },
]

describe('searchItems', () => {
  it('finds by part of the name with the price range', () => {
    expect(searchItems(items, 'חלב')).toEqual([
      { barcode: '7290000000001', name: 'חלב 3% קרטון', manufacturer: 'תנובה', min_price: 6.2, max_price: 6.9, store_count: 2 },
    ])
  })
  it('puts an exact barcode first', () => {
    expect(searchItems(items, '7290000000002')[0]?.barcode).toBe('7290000000002')
  })
})

describe('compareBasket', () => {
  it('ranks the most complete store first and lists what others miss', () => {
    const [best, other] = compareBasket(items, ['7290000000001', '7290000000002'])
    expect(best).toMatchObject({ chain: 'רמי לוי', total: 10.7, found: 2, missing: [] })
    expect(other).toMatchObject({ chain: 'אושר עד', total: 6.9, found: 1, missing: ['7290000000002'] })
  })
  it('filters by city', () => {
    expect(compareBasket(items, ['7290000000001'], 'מגדל העמק').map((s) => s.chain)).toEqual(['אושר עד'])
  })
})
