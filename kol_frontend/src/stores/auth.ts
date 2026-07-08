import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { getCurrentUser, loginLocal, TOKEN_KEY } from '../services/api'
import type { AuthResponse, User } from '../types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const initialized = ref(false)

  const isAuthenticated = computed(() => Boolean(token.value && user.value))
  const isKol = computed(() => user.value?.role === 'kol')

  function setSession(payload: AuthResponse) {
    token.value = payload.access_token
    user.value = payload.user
    localStorage.setItem(TOKEN_KEY, payload.access_token)
  }

  function clearSession() {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  async function login(email: string, password: string) {
    loading.value = true
    try {
      const response = await loginLocal(email, password)
      if (response.user.role !== 'kol') {
        clearSession()
        throw new Error('This workspace is only available for KOL accounts.')
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
        throw new Error('This workspace is only available for KOL accounts.')
      }
      user.value = currentUser
    } catch {
      clearSession()
    } finally {
      initialized.value = true
    }
  }

  function acceptOAuthToken(accessToken: string) {
    token.value = accessToken
    localStorage.setItem(TOKEN_KEY, accessToken)
  }

  async function finalizeOAuth() {
    const currentUser = await getCurrentUser()
    if (currentUser.role !== 'kol') {
      clearSession()
      throw new Error('Google login succeeded, but this account is not a KOL.')
    }

    user.value = currentUser
    initialized.value = true
  }

  function logout() {
    clearSession()
  }

  return {
    token,
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
