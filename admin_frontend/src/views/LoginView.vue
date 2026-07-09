<template>
  <div class="flex min-h-screen items-center justify-center p-4">
    <!-- Login Glass Card -->
    <div class="w-full max-w-md rounded-3xl border border-white/10 bg-slate-900/60 backdrop-blur-xl p-8 shadow-2xl relative overflow-hidden">
      <!-- Glowing bubble accent -->
      <div class="absolute -top-10 -right-10 w-36 h-36 rounded-full bg-indigo-500/10 blur-3xl" />
      <div class="absolute -bottom-10 -left-10 w-36 h-36 rounded-full bg-purple-500/10 blur-3xl" />

      <div class="mb-8 text-center relative">
        <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-500 text-xl font-bold text-white shadow-lg shadow-indigo-500/35">AB</div>
        <h1 class="text-2xl font-bold text-white">Admin Backoffice</h1>
        <p class="mt-2 text-xs text-slate-400">Đăng nhập để quản lý KOL, khách hàng và booking</p>
      </div>

      <!-- Google Login Option -->
      <a
        :href="googleUrl"
        class="mb-4 flex h-11 w-full items-center justify-center rounded-xl border border-white/10 bg-white/5 text-sm font-semibold text-slate-200 transition hover:bg-white/10 hover:text-white cursor-pointer"
      >
        Đăng nhập với Google
      </a>

      <div class="relative my-6 text-center text-xs uppercase tracking-wider text-slate-500 flex items-center justify-center gap-3">
        <div class="flex-1 h-px bg-white/5"></div>
        <span>hoặc</span>
        <div class="flex-1 h-px bg-white/5"></div>
      </div>

      <!-- Local Login Form -->
      <form class="space-y-4 relative" @submit.prevent="handleSubmit">
        <div>
          <label class="mb-2 block text-xs font-semibold text-slate-400">Email</label>
          <input v-model="email" type="email" required class="field" placeholder="admin@example.com" />
        </div>
        <div>
          <label class="mb-2 block text-xs font-semibold text-slate-400">Mật khẩu</label>
          <input v-model="password" type="password" required class="field" placeholder="••••••••" />
        </div>
        <label class="flex items-center gap-2 text-xs text-slate-400 cursor-pointer select-none">
          <input v-model="rememberMe" type="checkbox" class="h-4 w-4 rounded border-white/10 bg-black/20 text-indigo-600 focus:ring-0" />
          Ghi nhớ email
        </label>
        
        <p v-if="auth.error" class="rounded-xl bg-rose-500/10 border border-rose-500/20 px-4 py-3 text-xs text-rose-300">{{ auth.error }}</p>
        
        <button type="submit" class="btn-primary w-full" :disabled="auth.loading">
          {{ auth.loading ? "Đang xử lý..." : "Đăng nhập" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import { getGoogleOAuthUrl } from "@/api/auth";
import {
  clearRememberedCredentials,
  readRememberedCredentials,
  saveRememberedCredentials,
  useAuthStore,
} from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const remembered = readRememberedCredentials();
const email = ref(remembered?.email || "admin@example.com");
const password = ref("");
const rememberMe = ref(Boolean(remembered));
const googleUrl = getGoogleOAuthUrl();

async function handleSubmit() {
  try {
    await auth.login(email.value, password.value);
    if (rememberMe.value) {
      saveRememberedCredentials(email.value.trim());
    } else {
      clearRememberedCredentials();
    }
    router.push("/dashboard");
  } catch {
    // error handled in store
  }
}
</script>

<style scoped>
.field {
  @apply h-11 w-full rounded-xl border border-white/10 bg-black/25 px-4 text-sm text-white outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/10 placeholder:text-slate-500 transition;
}
.btn-primary {
  @apply h-11 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-bold text-sm shadow-lg shadow-indigo-500/25 transition cursor-pointer flex items-center justify-center active:scale-95 disabled:opacity-50;
}
</style>
