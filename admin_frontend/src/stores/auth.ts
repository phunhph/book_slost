import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { fetchMe, loginLocal } from "@/api/auth";
import { getErrorMessage } from "@/lib/errors";
import type { AuthUser } from "@/types";

const TOKEN_KEY = "abc_admin_access_token";
const TOKEN_META_KEY = "abc_admin_token_meta";
const CREDENTIALS_KEY = "abc_admin_credentials";
/** Admin workspace sessions: 1 day */
const DEFAULT_TTL_MS = 24 * 60 * 60 * 1000;

interface TokenMeta {
  expiresAt: number;
}

interface StoredCredentials {
  email: string;
}

function readToken(): string | null {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return null;
  const raw = localStorage.getItem(TOKEN_META_KEY);
  if (!raw) return token;
  try {
    const meta = JSON.parse(raw) as TokenMeta;
    if (meta.expiresAt && Date.now() >= meta.expiresAt) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(TOKEN_META_KEY);
      return null;
    }
  } catch {
    // keep token if meta is corrupt; hydrate will validate via API
  }
  return token;
}

export function readRememberedCredentials(): StoredCredentials | null {
  const raw = localStorage.getItem(CREDENTIALS_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as StoredCredentials & { password?: string };
    if (!parsed.email) return null;
    // Never keep plaintext passwords in localStorage (CodeQL / security).
    if (parsed.password) {
      localStorage.setItem(CREDENTIALS_KEY, JSON.stringify({ email: parsed.email }));
    }
    return { email: parsed.email };
  } catch {
    return null;
  }
}

export function saveRememberedCredentials(email: string) {
  localStorage.setItem(CREDENTIALS_KEY, JSON.stringify({ email }));
}

export function clearRememberedCredentials() {
  localStorage.removeItem(CREDENTIALS_KEY);
}

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(readToken());
  const expiresAt = ref<number | null>(null);
  const user = ref<AuthUser | null>(null);
  const loading = ref(false);
  const error = ref("");

  const isAuthenticated = computed(() => Boolean(token.value));
  const isAdmin = computed(() => user.value?.role === "admin");

  function persistToken(accessToken: string, expiresInSeconds?: number) {
    const ttlMs = (expiresInSeconds && expiresInSeconds > 0 ? expiresInSeconds : DEFAULT_TTL_MS / 1000) * 1000;
    token.value = accessToken;
    expiresAt.value = Date.now() + ttlMs;
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(TOKEN_META_KEY, JSON.stringify({ expiresAt: expiresAt.value }));
  }

  async function login(email: string, password: string) {
    loading.value = true;
    error.value = "";
    try {
      const response = await loginLocal(email, password);
      if (response.user.role !== "admin") {
        throw new Error("Tài khoản này không có quyền admin.");
      }
      persistToken(response.access_token, response.expires_in);
      user.value = response.user;
    } catch (err) {
      error.value = getErrorMessage(err, "Đăng nhập thất bại.");
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function hydrate() {
    if (!token.value) return;
    try {
      user.value = await fetchMe(token.value);
    } catch (err) {
      logout();
      throw new Error(getErrorMessage(err, "Không tải được phiên đăng nhập."));
    }
    if (user.value.role !== "admin") {
      logout();
      throw new Error("Tài khoản không có quyền admin.");
    }
  }

  function acceptOAuthToken(accessToken: string) {
    persistToken(accessToken, Math.floor(DEFAULT_TTL_MS / 1000));
  }

  function logout() {
    token.value = null;
    expiresAt.value = null;
    user.value = null;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(TOKEN_META_KEY);
  }

  return {
    token,
    expiresAt,
    user,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    login,
    hydrate,
    logout,
    acceptOAuthToken,
  };
});
