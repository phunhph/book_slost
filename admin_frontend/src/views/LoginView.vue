<template>
  <div class="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-[#2e59d9] p-4">
    <div class="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
      <div class="mb-8 text-center">
        <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--sb-primary)] text-xl font-bold text-white">AB</div>
        <h1 class="text-2xl font-bold text-slate-800">Admin Backoffice</h1>
        <p class="mt-2 text-sm text-slate-500">Dang nhap de quan ly KOL, khach hang va booking</p>
      </div>

      <a
        :href="googleUrl"
        class="mb-4 flex h-11 w-full items-center justify-center rounded-lg border border-slate-200 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
      >
        Dang nhap voi Google
      </a>

      <div class="relative my-6 text-center text-xs uppercase tracking-wider text-slate-400">
        <span class="bg-white px-3">hoac</span>
      </div>

      <form class="space-y-4" @submit.prevent="handleSubmit">
        <div>
          <label class="mb-2 block text-sm font-semibold text-slate-700">Email</label>
          <input v-model="email" type="email" required class="field" placeholder="admin@example.com" />
        </div>
        <div>
          <label class="mb-2 block text-sm font-semibold text-slate-700">Mat khau</label>
          <input v-model="password" type="password" required class="field" placeholder="••••••••" />
        </div>
        <p v-if="auth.error" class="rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ auth.error }}</p>
        <button type="submit" class="btn-primary w-full" :disabled="auth.loading">
          {{ auth.loading ? "Dang xu ly..." : "Dang nhap" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import { getGoogleOAuthUrl } from "@/api/auth";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const email = ref("admin@example.com");
const password = ref("Admin@123");
const googleUrl = getGoogleOAuthUrl();

async function handleSubmit() {
  try {
    await auth.login(email.value, password.value);
    router.push("/dashboard");
  } catch {
    // error handled in store
  }
}
</script>

<style scoped>
.field {
  @apply h-11 w-full rounded-lg border border-slate-200 px-4 text-sm outline-none focus:border-[var(--sb-primary)] focus:ring-2 focus:ring-blue-100;
}
.btn-primary {
  @apply h-11 rounded-lg bg-[var(--sb-primary)] text-sm font-bold text-white transition hover:bg-[var(--sb-primary-dark)] disabled:opacity-60;
}
</style>
