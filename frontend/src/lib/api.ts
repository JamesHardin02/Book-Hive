export class ApiError extends Error {
  status: number
  detail: unknown

  constructor(message: string, status: number, detail: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

function getApiBase(): string {
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
}

async function parseFastApiError(res: Response): Promise<unknown> {
  try {
    return await res.json()
  } catch {
    return { detail: `${res.status} ${res.statusText}` }
  }
}

/**
 * apiFetch:
 * - Always includes cookies (HttpOnly JWT cookie)
 * - Throws ApiError on non-2xx
 * - Returns parsed JSON (or null for 204)
 */
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${getApiBase()}${path}`

  const res = await fetch(url, {
    ...init,
    credentials: 'include',
  })

  if (res.status === 204) {
    return null as T
  }

  if (!res.ok) {
    const data = await parseFastApiError(res)
    // FastAPI commonly returns { detail: "..." } or { detail: [...] }
    const message =
      typeof (data as any)?.detail === 'string'
        ? (data as any).detail
        : `Request failed (${res.status})`
    throw new ApiError(message, res.status, data)
  }

  return (await res.json()) as T
}