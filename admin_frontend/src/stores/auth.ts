import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { fetchMe, loginLocal } from "@/api/auth";
import { getErrorMessage } from "@/lib/errors";
import type { AuthUser } from "@/types";

const TOKEN_KEY = "abc_access_token";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY));
  const user = ref<AuthUser | null>(null);
  const loading = ref(false);
  const error = ref("");

  const isAuthenticated = computed(() => Boolean(token.value));
  const isAdmin = computed(() => user.value?.role === "admin");

  async function login(email: string, password: string) {
    loading.value = true;
    error.value = "";
    try {
      const response = await loginLocal(email, password);
      if (response.user.role !== "admin") {
        throw new Error("Tài khoản này không có quyền admin.");
      }
      token.value = response.access_token;
      user.value = response.user;
      localStorage.setItem(TOKEN_KEY, response.access_token);
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

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem(TOKEN_KEY);
  }

  return { token, user, loading, error, isAuthenticated, isAdmin, login, hydrate, logout };
});
