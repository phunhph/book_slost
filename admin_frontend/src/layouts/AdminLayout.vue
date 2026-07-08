<template>
  <div class="min-h-screen bg-[var(--sb-bg)]">
    <aside
      class="fixed inset-y-0 left-0 z-30 w-[min(16rem,85vw)] -translate-x-full overflow-y-auto bg-[var(--sb-sidebar)] text-white transition-transform lg:w-64 lg:translate-x-0"
      :class="{ 'translate-x-0': sidebarOpen }"
      :aria-hidden="!sidebarOpen ? 'true' : undefined"
    >
      <div class="flex h-16 items-center border-b border-white/10 px-6">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--sb-primary)] font-bold">AB</div>
        <div class="ml-3">
          <p class="text-xs uppercase tracking-wider text-white/60">SB Admin</p>
          <p class="font-bold">Backoffice</p>
        </div>
      </div>
      <nav class="space-y-1 p-4">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-semibold text-white/80 transition hover:bg-[var(--sb-sidebar-hover)] hover:text-white"
          active-class="!bg-[var(--sb-primary)] !text-white"
          @click="sidebarOpen = false"
        >
          <span>{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </aside>

    <div v-if="sidebarOpen" class="fixed inset-0 z-20 bg-black/40 lg:hidden" @click="sidebarOpen = false" />

    <div class="lg:pl-64">
      <header class="sticky top-0 z-10 flex min-h-16 flex-wrap items-center justify-between gap-2 border-b border-[var(--sb-card-border)] bg-white px-4 py-3 shadow-sm sm:px-6">
        <button class="rounded-lg border px-3 py-2 text-sm lg:hidden" type="button" :aria-expanded="sidebarOpen" @click="sidebarOpen = !sidebarOpen">Menu</button>
        <div class="hidden text-sm text-slate-500 lg:block">Quản lý hệ thống Affiliate Booking</div>
        <div class="flex min-w-0 items-center gap-2 sm:gap-3">
          <span class="max-w-[10rem] truncate text-sm text-slate-600 sm:max-w-xs">{{ auth.user?.email }}</span>
          <button class="rounded-lg bg-[var(--sb-primary)] px-4 py-2 text-sm font-semibold text-white" @click="handleLogout">
            Đăng xuất
          </button>
        </div>
      </header>

      <main class="p-4 sm:p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { RouterLink, RouterView, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const sidebarOpen = ref(false);

watch(sidebarOpen, (open) => {
  document.body.style.overflow = open ? "hidden" : "";
});

const navItems = [
  { to: "/dashboard", label: "Tổng quan", icon: "📊" },
  { to: "/kols", label: "Danh sách KOL", icon: "⭐" },
  { to: "/customers", label: "Khách hàng", icon: "👥" },
  { to: "/bookings", label: "Booking", icon: "📅" }
];

function handleLogout() {
  auth.logout();
  router.push("/login");
}
</script>
