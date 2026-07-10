<template>
  <div class="min-h-screen bg-transparent p-4 lg:p-6">
    <!-- Floating Sidebar -->
    <aside
      class="fixed inset-y-4 left-4 z-30 w-64 -translate-x-full overflow-y-auto bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-3xl p-4 shadow-2xl transition-transform lg:translate-x-0 flex flex-col"
      :class="{ 'translate-x-0': sidebarOpen }"
      :aria-hidden="!sidebarOpen ? 'true' : undefined"
    >
      <!-- Sidebar Header -->
      <div class="flex items-center gap-3 px-2 py-4 mb-4 border-b border-white/5">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 font-bold text-white shadow-lg shadow-indigo-500/35">AB</div>
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.25em] text-indigo-300">Slost Admin</p>
          <p class="text-sm font-bold text-white">Backoffice</p>
        </div>
      </div>

      <!-- Navigation Menu -->
      <nav class="space-y-1.5 flex-1">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium text-slate-300 transition-all hover:bg-white/5 hover:text-white"
          active-class="!bg-gradient-to-r !from-indigo-600 !to-indigo-500 !text-white shadow-lg shadow-indigo-500/25"
          @click="sidebarOpen = false"
        >
          <span class="text-base">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <!-- Account Info Area -->
      <div class="mt-auto p-3.5 rounded-2xl bg-white/5 border border-white/5">
        <p class="text-[10px] uppercase tracking-wider text-slate-500">Tài khoản</p>
        <p class="truncate text-xs font-medium text-white mt-1">{{ auth.user?.email }}</p>
        <p class="text-[9px] text-indigo-300 mt-0.5 uppercase tracking-wider">Admin Role</p>
      </div>
    </aside>

    <!-- Overlay under Sidebar (mobile only) -->
    <div v-if="sidebarOpen" class="fixed inset-0 z-20 bg-slate-950/60 backdrop-blur-sm lg:hidden" @click="sidebarOpen = false" />

    <!-- Content Area wrapper -->
    <div class="lg:pl-72 flex flex-col min-h-screen">
      <!-- Page Header -->
      <header class="rounded-3xl border border-white/10 bg-slate-900/60 backdrop-blur-xl px-5 py-4 shadow-xl flex items-center justify-between gap-3">
        <button 
          class="rounded-xl border border-white/10 px-3 py-2 text-xs font-semibold bg-white/5 hover:bg-white/10 transition cursor-pointer lg:hidden" 
          type="button" 
          :aria-expanded="sidebarOpen" 
          @click="sidebarOpen = !sidebarOpen"
        >
          Menu
        </button>
        <div class="hidden text-xs font-bold text-slate-400 lg:block uppercase tracking-wider">Hệ thống quản lý Affiliate Booking</div>
        <div class="flex items-center gap-3 min-w-0">
          <span class="max-w-[10rem] truncate text-xs text-slate-300 sm:max-w-xs">{{ auth.user?.email }}</span>
          <button 
            class="rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 hover:text-white px-3 py-1.5 text-xs font-semibold transition cursor-pointer active:scale-95" 
            @click="handleLogout"
          >
            Đăng xuất
          </button>
        </div>
      </header>

      <!-- Main Content Page -->
      <main class="py-6 flex-1 min-w-0">
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
  { to: "/users", label: "Tài khoản", icon: "👥" },
  { to: "/platforms", label: "Nền tảng", icon: "🔗" },
  { to: "/bookings", label: "Booking", icon: "📅" }
];

function handleLogout() {
  auth.logout();
  router.push("/login");
}
</script>
