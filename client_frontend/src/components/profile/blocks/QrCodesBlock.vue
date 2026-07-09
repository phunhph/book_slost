<script setup lang="ts">
import type { QrCodeItem } from '@/types/profile'

defineProps<{
  items: QrCodeItem[]
}>()
</script>

<template>
  <section class="profile-section">
    <p class="profile-section__label">Mã QR</p>
    <div class="grid gap-3 grid-cols-2">
      <a
        v-for="(item, index) in items"
        :key="`${item.label}-${index}`"
        :href="item.target_url || item.image_url"
        target="_blank"
        rel="noreferrer"
        class="rounded-xl border border-current/12 bg-black/8 p-3 text-center transition hover:border-current/25"
      >
        <img :src="item.image_url" :alt="item.label" class="mx-auto h-28 w-28 object-contain" />
        <p class="mt-2 text-sm font-medium">{{ item.label }}</p>
      </a>
    </div>
  </section>
</template>
