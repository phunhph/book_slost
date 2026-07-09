<script setup lang="ts">
import type { KolPublicCard } from "@/types/profile";

const props = defineProps<{
  kol: KolPublicCard;
}>();

const fallbackName = props.kol.display_name ?? props.kol.username ?? "Creator chưa đặt tên";
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
        {{ kol.bio || 'Xem hồ sơ creator và gửi yêu cầu đặt lịch chơi cùng chỉ với vài thao tác.' }}
      </p>
      <div class="mt-4 rounded-2xl border border-white/10 bg-black/20 px-3 py-2 text-xs text-slate-200">
        <p>
          Theo trận:
          <strong>{{ new Intl.NumberFormat('vi-VN').format(kol.price_per_match || 0) }} {{ kol.currency || 'VND' }}</strong>
        </p>
        <p class="mt-1">
          Theo giờ:
          <strong>{{ new Intl.NumberFormat('vi-VN').format(kol.price_per_hour || 0) }} {{ kol.currency || 'VND' }}</strong>
        </p>
      </div>
      <div class="mt-6 flex items-center justify-between text-sm">
        <span class="rounded-full border border-white/10 px-3 py-1 text-slate-200">Hồ sơ công khai</span>
        <span class="font-medium text-white transition group-hover:text-sky-200">Xem chi tiết</span>
      </div>
    </div>
  </RouterLink>
</template>
