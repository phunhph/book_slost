<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import KolCard from "@/components/kols/KolCard.vue";
import { kolWorkspaceUrl } from "@/lib/appUrls";
import { getPublicKols } from "@/services/public";
import { useAuthStore } from "@/stores/auth";
import { useToastStore } from "@/stores/toast";
import type { KolPublicCard } from "@/types/profile";

const authStore = useAuthStore();
const toast = useToastStore();
const kols = ref<KolPublicCard[]>([]);
const isLoading = ref(true);
const loadFailed = ref(false);

const featuredKols = computed(() => kols.value.filter((item) => item.username));
const isKolAccount = computed(() => authStore.user?.role === "kol");

onMounted(async () => {
  try {
    kols.value = await getPublicKols();
  } catch (error) {
    loadFailed.value = true;
    toast.error(error instanceof Error ? error.message : "Unable to load creators.");
  } finally {
    isLoading.value = false;
  }
});
</script>

<template>
  <section class="page-container py-10 sm:py-16 lg:py-16">
    <div
      v-if="isKolAccount"
      class="mb-8 rounded-[2rem] border border-fuchsia-400/20 bg-fuchsia-500/10 p-5 text-fuchsia-50"
    >
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="text-sm font-semibold uppercase tracking-[0.28em] text-fuchsia-200">KOL account detected</p>
          <h2 class="mt-2 text-xl font-semibold text-white">Ban dang dang nhap bang tai khoan creator/KOL</h2>
          <p class="mt-2 text-sm leading-6 text-fuchsia-100/90">
            Public site nay chi de xem marketplace. De quan ly ca nhan va custom profile, hay mo KOL Workspace.
          </p>
        </div>
        <a
          :href="kolWorkspaceUrl('/dashboard', authStore.accessToken)"
          class="inline-flex items-center justify-center rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
        >
          Open KOL Workspace
        </a>
      </div>
    </div>

    <div class="grid gap-12 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.32em] text-sky-300">Public marketplace</p>
        <h1 class="mt-5 max-w-3xl text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
          Find KOLs with personality, clear style, and a booking flow built for mobile.
        </h1>
        <p class="mt-6 max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">
          Browse public creator pages, review custom profile themes, and send partnership requests without leaving the page.
        </p>
        <div class="mt-8 flex flex-wrap gap-3">
          <a href="#creators" class="rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200">Explore creators</a>
          <div class="rounded-full border border-white/12 px-5 py-3 text-sm text-slate-200">Login optional for guest bookings</div>
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
        <div class="theme-card rounded-[2rem] p-5">
          <p class="text-sm uppercase tracking-[0.24em] text-fuchsia-200">Fast workflow</p>
          <h2 class="mt-3 text-xl font-semibold text-white">Guest booking or logged-in autofill</h2>
          <p class="mt-3 text-sm leading-6 text-slate-300">Customers can sign in for profile-based autofill, while guests can still submit requests directly.</p>
        </div>
        <div class="theme-card rounded-[2rem] p-5">
          <p class="text-sm uppercase tracking-[0.24em] text-emerald-200">Custom profiles</p>
          <h2 class="mt-3 text-xl font-semibold text-white">Themed layouts with dynamic colors</h2>
          <p class="mt-3 text-sm leading-6 text-slate-300">Each creator detail page adapts to their chosen visual identity and block ordering.</p>
        </div>
      </div>
    </div>

    <section id="creators" class="mt-16">
      <div class="flex items-end justify-between gap-4">
        <div>
          <p class="text-sm uppercase tracking-[0.28em] text-sky-300">Creators</p>
          <h2 class="mt-3 text-3xl font-semibold text-white">Featured KOLs</h2>
        </div>
        <p class="hidden text-sm text-slate-400 sm:block">{{ featuredKols.length }} public profiles available</p>
      </div>

      <div v-if="isLoading" class="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div v-for="index in 6" :key="index" class="h-72 animate-pulse rounded-[2rem] border border-white/10 bg-white/5"></div>
      </div>

      <div v-else-if="loadFailed" class="mt-8 rounded-[2rem] border border-white/10 bg-white/6 p-6 text-slate-300">
        Không tải được danh sách creator. Vui lòng thử lại sau.
      </div>

      <div v-else-if="!featuredKols.length" class="mt-8 rounded-[2rem] border border-white/10 bg-white/6 p-6 text-slate-200">
        No public creators are available yet.
      </div>

      <div v-else class="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        <KolCard v-for="kol in featuredKols" :key="kol.user_id" :kol="kol" />
      </div>
    </section>
  </section>
</template>
