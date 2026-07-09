<script setup lang="ts">
import type { QrCodeItem } from '@/types/profile'

defineProps<{
  items: QrCodeItem[]
}>()
</script>

<template>
  <section class="profile-section">
    <p class="profile-section__label">Mã QR</p>
    
    <div class="grid gap-5 grid-cols-1 sm:grid-cols-2 max-w-2xl mx-auto mt-4">
      <a
        v-for="(item, index) in items"
        :key="`${item.label}-${index}`"
        :href="item.target_url || item.image_url"
        target="_blank"
        rel="noreferrer"
        class="group rounded-3xl border border-white/8 bg-slate-900/40 backdrop-blur-xl p-5 text-center shadow-lg transition-all duration-300 hover:border-indigo-500/50 hover:bg-slate-900/60 hover:-translate-y-1"
      >
        <div class="mx-auto h-44 w-44 sm:h-48 sm:w-48 rounded-2xl bg-white p-3.5 shadow-md flex items-center justify-center border border-white/5 transition group-hover:scale-[1.02]">
          <img :src="item.image_url" :alt="item.label" class="h-full w-full object-contain" />
        </div>
        <p class="mt-3 text-sm font-bold text-slate-200 group-hover:text-white transition">{{ item.label }}</p>
        <p v-if="item.target_url" class="mt-1 text-[10px] text-slate-400 opacity-60">Nhấp để mở liên kết ứng dụng</p>
      </a>
    </div>
  </section>
</template>
