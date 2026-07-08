<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import { getGoogleOAuthUrl } from "@/services/auth";
import { redirectByRole, shouldRedirectAuthenticatedRole } from "@/lib/appUrls";
import { useAuthStore } from "@/stores/auth";
import { useToastStore } from "@/stores/toast";

type AuthMode = "login" | "register";

const props = defineProps<{
  isOpen: boolean;
  initialMode: AuthMode;
}>();

const emit = defineEmits<{
  close: [];
  authenticated: [];
}>();

const authStore = useAuthStore();
const toast = useToastStore();
const route = useRoute();
const mode = ref<AuthMode>(props.initialMode);
const email = ref("");
const password = ref("");
const displayName = ref("");
const username = ref("");
const isSubmitting = ref(false);

watch(
  () => props.initialMode,
  (value) => {
    mode.value = value;
  },
  { immediate: true },
);

const googleUrl = computed(() => getGoogleOAuthUrl());

watch(
  () => props.isOpen,
  (open) => {
    document.body.style.overflow = open ? "hidden" : "";
  },
  { immediate: true },
);

onUnmounted(() => {
  document.body.style.overflow = "";
});

async function submit() {
  isSubmitting.value = true;

  try {
    if (mode.value === "login") {
      const response = await authStore.login({
        email: email.value.trim(),
        password: password.value,
      });
      if (authStore.user && shouldRedirectAuthenticatedRole(authStore.user.role, route.path)) {
        redirectByRole(authStore.user.role, authStore.accessToken);
        return;
      }
      toast.success(response.message);
    } else {
      const response = await authStore.register({
        email: email.value.trim(),
        password: password.value,
        display_name: displayName.value.trim() || undefined,
        username: username.value.trim() || undefined,
      });
      if (authStore.user && shouldRedirectAuthenticatedRole(authStore.user.role, route.path)) {
        redirectByRole(authStore.user.role, authStore.accessToken);
        return;
      }
      toast.success(response.message);
    }

    emit("authenticated");
  } catch (error) {
    toast.error(error instanceof Error ? error.message : "Authentication failed.");
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-slate-950/70 px-4 py-6 backdrop-blur-sm sm:items-center sm:py-10"
      role="dialog"
      aria-modal="true"
      @click.self="emit('close')"
    >
      <div class="my-auto w-full max-w-md max-h-[min(90dvh,calc(100vh-3rem))] overflow-y-auto rounded-[2rem] border border-white/12 bg-slate-950 p-5 shadow-2xl shadow-sky-950/40 sm:p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm uppercase tracking-[0.3em] text-sky-300">Customer access</p>
            <h2 class="mt-2 text-2xl font-semibold text-white">{{ mode === 'login' ? 'Welcome back' : 'Create your account' }}</h2>
          </div>
          <button class="rounded-full border border-white/10 px-3 py-2 text-sm text-slate-300 hover:bg-white/6" type="button" @click="emit('close')">Close</button>
        </div>

        <div class="mt-6 flex rounded-full border border-white/10 bg-white/5 p-1">
          <button
            class="flex-1 rounded-full px-4 py-2 text-sm font-medium transition"
            :class="mode === 'login' ? 'bg-white text-slate-900' : 'text-slate-300'"
            type="button"
            @click="mode = 'login'"
          >
            Login
          </button>
          <button
            class="flex-1 rounded-full px-4 py-2 text-sm font-medium transition"
            :class="mode === 'register' ? 'bg-white text-slate-900' : 'text-slate-300'"
            type="button"
            @click="mode = 'register'"
          >
            Register
          </button>
        </div>

        <form class="mt-6 space-y-4" @submit.prevent="submit">
          <div v-if="mode === 'register'" class="grid gap-4 sm:grid-cols-2">
            <label class="block text-sm text-slate-200">
              <span class="mb-2 block">Display name</span>
              <input v-model="displayName" class="w-full rounded-2xl border border-white/12 bg-white/5 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-500 focus:border-sky-400" placeholder="Jane Doe" type="text" />
            </label>
            <label class="block text-sm text-slate-200">
              <span class="mb-2 block">Username</span>
              <input v-model="username" class="w-full rounded-2xl border border-white/12 bg-white/5 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-500 focus:border-sky-400" placeholder="janedoe" type="text" />
            </label>
          </div>

          <label class="block text-sm text-slate-200">
            <span class="mb-2 block">Email</span>
            <input v-model="email" class="w-full rounded-2xl border border-white/12 bg-white/5 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-500 focus:border-sky-400" placeholder="you@example.com" type="email" required />
          </label>

          <label class="block text-sm text-slate-200">
            <span class="mb-2 block">Password</span>
            <input v-model="password" class="w-full rounded-2xl border border-white/12 bg-white/5 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-500 focus:border-sky-400" placeholder="Minimum 8 characters" type="password" minlength="8" required />
          </label>

          <button class="w-full rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? 'Please wait...' : mode === 'login' ? 'Login' : 'Create account' }}
          </button>
        </form>

        <div class="my-6 flex items-center gap-4 text-xs uppercase tracking-[0.24em] text-slate-500">
          <span class="h-px flex-1 bg-white/10"></span>
          <span>or continue with</span>
          <span class="h-px flex-1 bg-white/10"></span>
        </div>

        <a :href="googleUrl" class="flex items-center justify-center rounded-2xl border border-white/12 px-4 py-3 text-sm font-medium text-white transition hover:border-white/25 hover:bg-white/6">
          Google OAuth
        </a>
      </div>
    </div>
  </Teleport>
</template>
