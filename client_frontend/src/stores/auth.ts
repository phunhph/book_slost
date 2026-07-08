import { defineStore } from "pinia";

import { fetchCurrentUser, fetchProfileByUserId, loginLocal, registerLocal } from "@/services/auth";
import type { AuthUser, LoginPayload, RegisterPayload } from "@/types/auth";
import type { UserProfile } from "@/types/profile";

const STORAGE_KEY = "slost-client-auth";
const CREDENTIALS_KEY = "slost-client-credentials";
/** Client sessions expire after 1 hour */
const DEFAULT_TTL_MS = 60 * 60 * 1000;

interface StoredAuthState {
  accessToken: string | null;
  expiresAt: number | null;
}

interface StoredCredentials {
  email: string;
  password: string;
}

function readStoredAuth(): StoredAuthState {
  if (typeof window === "undefined") {
    return { accessToken: null, expiresAt: null };
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return { accessToken: null, expiresAt: null };
  }

  try {
    const parsed = JSON.parse(raw) as StoredAuthState;
    if (parsed.expiresAt && Date.now() >= parsed.expiresAt) {
      window.localStorage.removeItem(STORAGE_KEY);
      return { accessToken: null, expiresAt: null };
    }
    return {
      accessToken: parsed.accessToken ?? null,
      expiresAt: parsed.expiresAt ?? null,
    };
  } catch {
    return { accessToken: null, expiresAt: null };
  }
}

export function readRememberedCredentials(): StoredCredentials | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(CREDENTIALS_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as StoredCredentials;
    if (!parsed.email || !parsed.password) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function saveRememberedCredentials(email: string, password: string) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(CREDENTIALS_KEY, JSON.stringify({ email, password }));
}

export function clearRememberedCredentials() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(CREDENTIALS_KEY);
}

let initializePromise: Promise<void> | null = null;

export const useAuthStore = defineStore("auth", {
  state: () => {
    const stored = readStoredAuth();
    return {
      accessToken: stored.accessToken as string | null,
      expiresAt: stored.expiresAt as number | null,
      user: null as AuthUser | null,
      userProfile: null as UserProfile | null,
      isInitializing: false,
      isReady: false,
    };
  },
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken && state.user),
    /** Token still present while /me is loading after refresh */
    hasStoredSession: (state) => Boolean(state.accessToken),
  },
  actions: {
    persist() {
      if (typeof window === "undefined") {
        return;
      }

      if (!this.accessToken) {
        window.localStorage.removeItem(STORAGE_KEY);
        return;
      }

      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          accessToken: this.accessToken,
          expiresAt: this.expiresAt,
        }),
      );
    },
    setToken(token: string, expiresInSeconds?: number) {
      const ttlMs = (expiresInSeconds && expiresInSeconds > 0 ? expiresInSeconds : 3600) * 1000;
      this.accessToken = token;
      this.expiresAt = Date.now() + ttlMs;
      this.persist();
    },
    async hydrateUser(token: string, expiresInSeconds?: number) {
      const user = await fetchCurrentUser(token);
      this.user = user;
      this.userProfile = await fetchProfileByUserId(user.id, token).catch(() => null);
      this.setToken(token, expiresInSeconds ?? Math.floor(DEFAULT_TTL_MS / 1000));
    },
    async initialize() {
      if (this.isReady) {
        return;
      }
      if (initializePromise) {
        return initializePromise;
      }

      initializePromise = (async () => {
        this.isInitializing = true;
        try {
          const stored = readStoredAuth();
          if (!stored.accessToken) {
            this.accessToken = null;
            this.expiresAt = null;
            return;
          }

          this.accessToken = stored.accessToken;
          this.expiresAt = stored.expiresAt;

          const remainingSeconds = stored.expiresAt
            ? Math.max(1, Math.floor((stored.expiresAt - Date.now()) / 1000))
            : Math.floor(DEFAULT_TTL_MS / 1000);

          try {
            await this.hydrateUser(stored.accessToken, remainingSeconds);
          } catch {
            this.logout();
          }
        } finally {
          this.isInitializing = false;
          this.isReady = true;
          initializePromise = null;
        }
      })();

      return initializePromise;
    },
    async login(payload: LoginPayload) {
      const response = await loginLocal(payload);
      await this.hydrateUser(response.access_token, response.expires_in);
      this.isReady = true;
      return response;
    },
    async register(payload: RegisterPayload) {
      const response = await registerLocal(payload);
      await this.hydrateUser(response.access_token, response.expires_in);
      this.isReady = true;
      return response;
    },
    async completeGoogleLogin(accessToken: string) {
      await this.hydrateUser(accessToken, Math.floor(DEFAULT_TTL_MS / 1000));
      this.isReady = true;
    },
    logout() {
      this.accessToken = null;
      this.expiresAt = null;
      this.user = null;
      this.userProfile = null;
      this.isReady = true;
      if (typeof window !== "undefined") {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    },
  },
});
