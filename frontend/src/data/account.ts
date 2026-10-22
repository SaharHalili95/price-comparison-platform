// Signed-in features need the real API and a Google OAuth client ID; the static demo has neither.
const apiUrl = import.meta.env.VITE_API_URL as string | undefined
export const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined
export const accountsEnabled = Boolean(apiUrl && googleClientId)

const KEY = 'salsmart.token'

export interface Alert {
  id: number
  barcode: string
  name: string
  target_price: number | null
  current_min_price: number | null
}

export const getToken = () => localStorage.getItem(KEY)
export const signOut = () => localStorage.removeItem(KEY)

async function call<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken() ?? ''}`, ...init.headers },
  })
  if (response.status === 401) signOut()
  if (!response.ok) throw new Error(`${response.status}`)
  return (response.status === 204 ? undefined : await response.json()) as T
}

export async function signInWithGoogle(credential: string): Promise<void> {
  const tokens = await call<{ access_token: string }>('/auth/google', { method: 'POST', body: JSON.stringify({ credential }) })
  localStorage.setItem(KEY, tokens.access_token)
}

export const listAlerts = () => call<Alert[]>('/alerts')
export const createAlert = (barcode: string, targetPrice?: number) =>
  call<{ id: number }>('/alerts', { method: 'POST', body: JSON.stringify({ barcode, target_price: targetPrice ?? null }) })
export const deleteAlert = (id: number) => call<void>(`/alerts/${id}`, { method: 'DELETE' })
