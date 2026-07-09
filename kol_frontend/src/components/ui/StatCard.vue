<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  caption?: string
}>()
</script>

<template>
  <div class="workspace-card workspace-card--soft">
    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{{ label }}</p>
    <p class="mt-3 text-3xl font-semibold text-white sm:text-4xl">{{ value }}</p>
    <p v-if="caption" class="mt-2 text-sm leading-6 text-slate-400">{{ caption }}</p>
  </div>
</template>
