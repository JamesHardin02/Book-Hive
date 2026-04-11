import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

type UserPublic = {
  id: number
  username: string
  email: string
  is_active: boolean
  is_admin: boolean
}

// FastAPI's 422 Validation Error schema (unprocessable inputs) for register and login
export interface ValidationErrorDetail {
  type: string
  loc: (string | number)[]
  msg: string
  input?: string
  ctx?: Record<string, number>
}

function getApiBase(): string {
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
}

async function parseError(res: Response): Promise<string | ValidationErrorDetail[]> {
  try {
    const data = await res.json()
    if (Array.isArray(data?.detail)) return data.detail as ValidationErrorDetail[]
    if (typeof data?.detail === 'string') return data.detail
    return JSON.stringify(data)
  } catch {
    return `${res.status} ${res.statusText}`
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserPublic | null>(null)
  const initialized = ref(false)
  const loading = ref(false)
  const error = ref<ValidationErrorDetail[] | string | null>(null)

  const isAuthenticated = computed(() => user.value !== null)

  let initPromise: Promise<void> | null = null

  async function fetchMe(): Promise<void> {
    const res = await fetch(`${getApiBase()}/auth/me`, {
      credentials: 'include',
    })

    if (!res.ok) {
      user.value = null
      return
    }

    user.value = (await res.json()) as UserPublic
  }

  async function init(): Promise<void> {
    if (initialized.value) return
    if (initPromise) return initPromise

    initPromise = (async () => {
      try {
        await fetchMe()
      } finally {
        initialized.value = true
        initPromise = null
      }
    })()

    return initPromise
  }

  async function login(email: string, password: string): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const body = new URLSearchParams()
      body.set('username', email)
      body.set('password', password)

      const res = await fetch(`${getApiBase()}/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body,
        credentials: 'include',
      })

      if (!res.ok) {
        error.value = await parseError(res)
        throw new Error('Login failed')
      }

      await fetchMe()
      initialized.value = true
    } finally {
      loading.value = false
    }
  }

  async function register(username: string, email: string, password: string): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const res = await fetch(`${getApiBase()}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
        credentials: 'include',
      })

      if (!res.ok) {
        error.value = await parseError(res)
        throw new Error('Registration failed')
      }
    } finally {
      loading.value = false
    }
  }

  async function logout(): Promise<void> {
    error.value = null
    user.value = null
    initialized.value = true

    await fetch(`${getApiBase()}/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    })
  }

  return {
    user,
    initialized,
    loading,
    error,
    isAuthenticated,
    init,
    login,
    register,
    fetchMe,
    logout,
  }
})
