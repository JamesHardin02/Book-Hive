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

// An array of many items that are arranged in the above schema structure
export interface ValidationErrorResponse {
  detail: ValidationErrorDetail[]
}

const TOKEN_KEY = 'bookhive_token'

function getApiBase(): string {
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
}

async function parseError(res: Response): Promise<string | ValidationErrorDetail[]> {
  try {
    const data = await res.json()

    // FastAPI validation error
    if (Array.isArray(data?.detail)) {
      return data.detail as ValidationErrorDetail[]
    }

    // FastAPI simple error: { detail: "message" }
    if (typeof data?.detail === 'string') {
      return data.detail
    }

    return JSON.stringify(data)
  } catch {
    return `${res.status} ${res.statusText}`
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const user = ref<UserPublic | null>(null)
  const initialized = ref(false)
  const loading = ref(false)
  const error = ref<ValidationErrorDetail[] | string | null>(null)

  const isAuthenticated = computed(() => Boolean(token.value))

  // localstorage stores token for MVP. Better to upgrade to HttpOnly cookies later
  function setToken(newToken: string | null) {
    token.value = newToken
    if (newToken) localStorage.setItem(TOKEN_KEY, newToken)
    else localStorage.removeItem(TOKEN_KEY)
  }

  async function fetchMe(): Promise<void> {
    if (!token.value) {
      user.value = null
      return
    }

    const res = await fetch(`${getApiBase()}/auth/me`, {
      headers: { Authorization: `Bearer ${token.value}` },
    })

    if (!res.ok) {
      setToken(null)
      user.value = null
      return
    }

    user.value = (await res.json()) as UserPublic
  }

  async function init(): Promise<void> {
    if (initialized.value) return
    initialized.value = true

    const saved = localStorage.getItem(TOKEN_KEY)
    if (saved) {
      token.value = saved
      await fetchMe()
    }
  }

  async function login(email: string, password: string): Promise<void> {
    loading.value = true
    error.value = null

    try {
      //OAuth2PasswordRequestForm requires x-www-form-urlencoded
      const body = new URLSearchParams()
      body.set('username', email) // backend treats username field as EMAIL
      body.set('password', password)

      const res = await fetch(`${getApiBase()}/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body,
      })

      if (!res.ok) {
        const parsed = await parseError(res)
        error.value = parsed
        throw new Error('Login failed')
      }

      const data = (await res.json()) as { access_token: string }
      setToken(data.access_token)
      await fetchMe()
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
      })

      if (!res.ok) {
        const parsed = await parseError(res)
        error.value = parsed
        throw new Error('Registration failed')
      }
    } finally {
      loading.value = false
    }
  }

  function logout(): void {
    error.value = null
    user.value = null
    setToken(null)
  }

  return {
    token,
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
