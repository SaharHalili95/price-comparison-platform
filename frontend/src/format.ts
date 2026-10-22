const money = new Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS' })
const day = new Intl.DateTimeFormat('he-IL', { day: '2-digit', month: '2-digit', year: 'numeric' })

export const shekel = (value: number) => money.format(value)
export const date = (iso: string) => day.format(new Date(iso))
