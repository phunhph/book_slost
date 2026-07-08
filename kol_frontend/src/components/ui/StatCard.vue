<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  caption?: string
}>()
</script>

<template>
  <div class="glass-panel rounded-3xl p-4 sm:p-5">
    <p class="text-sm text-slate-300">{{ label }}</p>
    <p class="mt-3 text-2xl font-semibold text-white sm:text-3xl">{{ value }}</p>
    <p v-if="caption" class="mt-2 text-sm text-slate-400">{{ caption }}</p>
  </div>
</template>
