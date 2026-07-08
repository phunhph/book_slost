<script setup lang="ts">
import type { KolPublicCard } from "@/types/profile";

const props = defineProps<{
  kol: KolPublicCard;
}>();

const fallbackName = props.kol.display_name ?? props.kol.username ?? "Unnamed creator";
</script>

<template>
  <RouterLink
    :to="kol.username ? `/kol/${kol.username}` : '/'"
    class="group relative overflow-hidden rounded-[2rem] border border-white/10 bg-white/6 p-6 transition duration-300 hover:-translate-y-1 hover:border-white/20 hover:bg-white/10"
  >
    <div class="absolute inset-x-6 top-0 h-24 rounded-b-full opacity-80 blur-3xl" :style="{ background: kol.primary_color ?? '#38bdf8' }"></div>
    <div class="relative">
      <div class="flex items-center gap-4">
        <div class="h-16 w-16 overflow-hidden rounded-2xl border border-white/10 bg-slate-900/70">
          <img v-if="kol.avatar_url" :src="kol.avatar_url" :alt="fallbackName" class="h-full w-full object-cover" />
          <div v-else class="flex h-full w-full items-center justify-center text-lg font-semibold text-slate-300">
            {{ fallbackName.slice(0, 1).toUpperCase() }}
          </div>
        </div>
        <div class="min-w-0 flex-1">
          <h3 class="truncate text-xl font-semibold text-white">{{ fallbackName }}</h3>
          <p class="mt-1 truncate text-sm text-sky-200">@{{ kol.username ?? 'creator' }}</p>
        </div>
      </div>
      <p class="mt-5 line-clamp-3 text-sm leading-6 text-slate-200/85">
        {{ kol.bio || 'Explore this creator profile, review the media kit, and send a booking request in a few taps.' }}
      </p>
      <div class="mt-6 flex items-center justify-between text-sm">
        <span class="rounded-full border border-white/10 px-3 py-1 text-slate-200">Public profile</span>
        <span class="font-medium text-white transition group-hover:text-sky-200">View details</span>
      </div>
    </div>
  </RouterLink>
</template>
