<script setup lang="ts">
import { computed, ref } from "vue";

import type { AuthUser } from "@/types/auth";
import type { UserProfile } from "@/types/profile";
import { kolWorkspaceUrl } from "@/lib/appUrls";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const menuOpen = ref(false);

const props = defineProps<{
  isAuthenticated: boolean;
  currentUser: AuthUser | UserProfile | null;
  authUser: AuthUser | null;
  isKolAccount: boolean;
}>();

const emit = defineEmits<{
  openAuth: [mode: "login" | "register"];
  logout: [];
}>();

const displayName = computed(() => {
  return (props.currentUser as UserProfile | null)?.display_name || (props.currentUser as AuthUser | null)?.email || "Tài khoản";
});

function closeMenu() {
  menuOpen.value = false;
}

function handleOpenAuth(mode: "login" | "register") {
  closeMenu();
  emit("openAuth", mode);
}

function handleLogout() {
  closeMenu();
  emit("logout");
}
</script>

<template>
  <header class="sticky top-0 z-40 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl pt-[env(safe-area-inset-top)]">
    <div class="page-container flex items-center justify-between gap-3 py-3 sm:gap-4 sm:py-4">
      <RouterLink to="/" class="flex min-w-0 items-center gap-3" @click="closeMenu">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-fuchsia-500 via-pink-500 to-sky-400 text-lg font-semibold text-white shadow-lg shadow-fuchsia-500/30 sm:h-11 sm:w-11">
          S
        </div>
        <div class="min-w-0">
          <p class="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300 sm:text-sm">Slost</p>
          <p class="truncate text-base font-semibold text-white sm:text-lg">Đặt lịch KOL nổi bật</p>
        </div>
      </RouterLink>

      <nav class="hidden items-center gap-2 sm:flex sm:gap-3">
        <template v-if="isAuthenticated">
          <a
            v-if="isKolAccount"
            :href="kolWorkspaceUrl('/dashboard', authStore.accessToken)"
            class="rounded-full border border-fuchsia-400/20 bg-fuchsia-400/10 px-4 py-2 text-sm font-medium text-fuchsia-100 transition hover:border-fuchsia-300/35 hover:bg-fuchsia-400/15"
          >
            Không gian KOL
          </a>
          <div class="max-w-[12rem] truncate rounded-full border border-emerald-400/20 bg-emerald-400/10 px-4 py-2 text-sm text-emerald-100 lg:max-w-xs">
            {{ displayName }}
          </div>
          <div
            v-if="authUser?.role"
            class="hidden rounded-full border border-sky-400/20 bg-sky-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-sky-100 lg:block"
          >
            {{ authUser.role }}
          </div>
          <button
            class="rounded-full border border-white/15 px-4 py-2 text-sm font-medium text-white transition hover:border-white/30 hover:bg-white/8"
            type="button"
            @click="handleLogout"
          >
            Đăng xuất
          </button>
        </template>
        <template v-else>
          <button
            class="rounded-full border border-white/15 px-4 py-2 text-sm font-medium text-white transition hover:border-white/30 hover:bg-white/8"
            type="button"
            @click="emit('openAuth', 'login')"
          >
            Đăng nhập
          </button>
          <button
            class="rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-slate-200"
            type="button"
            @click="emit('openAuth', 'register')"
          >
            Đăng ký
          </button>
        </template>
      </nav>

      <button
        class="flex size-10 items-center justify-center rounded-full border border-white/15 text-white transition hover:bg-white/8 sm:hidden"
        type="button"
        :aria-expanded="menuOpen"
        aria-controls="mobile-nav-panel"
        @click="menuOpen = !menuOpen"
      >
        <span class="sr-only">Mở menu</span>
        <svg v-if="!menuOpen" class="size-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
        <svg v-else class="size-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <div
      v-if="menuOpen"
      id="mobile-nav-panel"
      class="page-container border-t border-white/10 bg-slate-950/95 py-4 sm:hidden"
    >
      <div class="flex flex-col gap-3">
        <template v-if="isAuthenticated">
          <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
            <p class="truncate text-sm font-medium text-white">{{ displayName }}</p>
            <p v-if="authUser?.role" class="mt-1 text-xs uppercase tracking-[0.18em] text-sky-200">{{ authUser.role }}</p>
          </div>
          <a
            v-if="isKolAccount"
            :href="kolWorkspaceUrl('/dashboard', authStore.accessToken)"
            class="rounded-2xl border border-fuchsia-400/20 bg-fuchsia-400/10 px-4 py-3 text-center text-sm font-medium text-fuchsia-100"
            @click="closeMenu"
          >
            Mở không gian KOL
          </a>
          <button
            class="rounded-2xl border border-white/15 px-4 py-3 text-sm font-medium text-white"
            type="button"
            @click="handleLogout"
          >
            Đăng xuất
          </button>
        </template>
        <template v-else>
          <button
            class="rounded-2xl border border-white/15 px-4 py-3 text-sm font-medium text-white"
            type="button"
            @click="handleOpenAuth('login')"
          >
            Đăng nhập
          </button>
          <button
            class="rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-slate-900"
            type="button"
            @click="handleOpenAuth('register')"
          >
            Đăng ký
          </button>
        </template>
      </div>
    </div>
  </header>
</template>
