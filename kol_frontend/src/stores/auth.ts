import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { getCurrentUser, loginLocal, TOKEN_KEY } from '../services/api'
import type { AuthResponse, User } from '../types'

const TOKEN_META_KEY = `${TOKEN_KEY}_meta`
const CREDENTIALS_KEY = 'kol_remembered_credentials'
/** KOL workspace sessions: 1 day */
const DEFAULT_TTL_MS = 24 * 60 * 60 * 1000

interface TokenMeta {
  expiresAt: number
}

interface StoredCredentials {
  email: string
  password: string
}

function readToken(): string | null {
  const token = localStorage.getItem(TOKEN_KEY)
  if (!token) return null
  const raw = localStorage.getItem(TOKEN_META_KEY)
  if (!raw) return token
  try {
    const meta = JSON.parse(raw) as TokenMeta
    if (meta.expiresAt && Date.now() >= meta.expiresAt) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(TOKEN_META_KEY)
      return null
    }
  } catch {
    // ignore corrupt meta
  }
  return token
}

export function readRememberedCredentials(): StoredCredentials | null {
  const raw = localStorage.getItem(CREDENTIALS_KEY)
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw) as StoredCredentials
    if (!parsed.email || !parsed.password) return null
    return parsed
  } catch {
    return null
  }
}

export function saveRememberedCredentials(email: string, password: string) {
  localStorage.setItem(CREDENTIALS_KEY, JSON.stringify({ email, password }))
}

export function clearRememberedCredentials() {
  localStorage.removeItem(CREDENTIALS_KEY)
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(readToken())
  const expiresAt = ref<number | null>(null)
  const user = ref<User | null>(null)
  const loading = ref(false)
  const initialized = ref(false)

  const isAuthenticated = computed(() => Boolean(token.value && user.value))
  const isKol = computed(() => user.value?.role === 'kol')

  function persistToken(accessToken: string, expiresInSeconds?: number) {
    const ttlMs =
      (expiresInSeconds && expiresInSeconds > 0 ? expiresInSeconds : DEFAULT_TTL_MS / 1000) * 1000
    token.value = accessToken
    expiresAt.value = Date.now() + ttlMs
    localStorage.setItem(TOKEN_KEY, accessToken)
    localStorage.setItem(TOKEN_META_KEY, JSON.stringify({ expiresAt: expiresAt.value }))
  }

  function setSession(payload: AuthResponse) {
    persistToken(payload.access_token, payload.expires_in)
    user.value = payload.user
  }

  function clearSession() {
    token.value = null
    expiresAt.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(TOKEN_META_KEY)
  }

  async function login(email: string, password: string) {
    loading.value = true
    try {
      const response = await loginLocal(email, password)
      if (response.user.role !== 'kol') {
        clearSession()
        throw new Error('Không gian làm việc này chỉ dành cho tài khoản KOL.')
      }

      setSession(response)
      return response
    } finally {
      loading.value = false
    }
  }

  async function hydrate() {
    if (!token.value) {
      initialized.value = true
      return
    }

    try {
      const currentUser = await getCurrentUser()
      if (currentUser.role !== 'kol') {
        throw new Error('Không gian làm việc này chỉ dành cho tài khoản KOL.')
      }
      user.value = currentUser
    } catch {
      clearSession()
    } finally {
      initialized.value = true
    }
  }

  function acceptOAuthToken(accessToken: string) {
    persistToken(accessToken, Math.floor(DEFAULT_TTL_MS / 1000))
  }

  async function finalizeOAuth() {
    const currentUser = await getCurrentUser()
    if (currentUser.role !== 'kol') {
      clearSession()
      throw new Error('Đăng nhập Google thành công, nhưng tài khoản này không phải KOL.')
    }

    user.value = currentUser
    initialized.value = true
  }

  function logout() {
    clearSession()
  }

  return {
    token,
    expiresAt,
    user,
    loading,
    initialized,
    isAuthenticated,
    isKol,
    login,
    hydrate,
    logout,
    acceptOAuthToken,
    finalizeOAuth,
  }
})
