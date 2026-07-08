import { defineStore } from "pinia";

import { fetchCurrentUser, fetchProfileByUserId, loginLocal, registerLocal } from "@/services/auth";
import type { AuthUser, LoginPayload, RegisterPayload } from "@/types/auth";
import type { UserProfile } from "@/types/profile";

const STORAGE_KEY = "slost-client-auth";

interface StoredAuthState {
  accessToken: string | null;
}

function readStoredAuth(): StoredAuthState {
  if (typeof window === "undefined") {
    return { accessToken: null };
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return { accessToken: null };
  }

  try {
    return JSON.parse(raw) as StoredAuthState;
  } catch {
    return { accessToken: null };
  }
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    accessToken: null as string | null,
    user: null as AuthUser | null,
    userProfile: null as UserProfile | null,
    isInitializing: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken && state.user),
  },
  actions: {
    persist() {
      if (typeof window === "undefined") {
        return;
      }

      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          accessToken: this.accessToken,
        }),
      );
    },
    async hydrateUser(token: string) {
      this.isInitializing = true;
      try {
        const user = await fetchCurrentUser(token);
        this.user = user;
        this.userProfile = await fetchProfileByUserId(user.id, token).catch(() => null);
        this.accessToken = token;
        this.persist();
      } catch (error) {
        this.logout();
        throw error;
      } finally {
        this.isInitializing = false;
      }
    },
    async initialize() {
      if (this.user || this.isInitializing) {
        return;
      }

      const stored = readStoredAuth();
      if (!stored.accessToken) {
        return;
      }

      await this.hydrateUser(stored.accessToken).catch(() => undefined);
    },
    async login(payload: LoginPayload) {
      const response = await loginLocal(payload);
      await this.hydrateUser(response.access_token);
      return response;
    },
    async register(payload: RegisterPayload) {
      const response = await registerLocal(payload);
      await this.hydrateUser(response.access_token);
      return response;
    },
    async completeGoogleLogin(accessToken: string) {
      await this.hydrateUser(accessToken);
    },
    logout() {
      this.accessToken = null;
      this.user = null;
      this.userProfile = null;
      if (typeof window !== "undefined") {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    },
  },
});
