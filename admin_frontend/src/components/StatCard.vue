<template>
  <div class="rounded-xl border-l-4 bg-white p-5 card-shadow" :class="borderClass">
    <div class="text-xs font-bold uppercase tracking-wider" :class="textClass">{{ label }}</div>
    <div class="mt-2 text-2xl font-bold text-slate-800">{{ value }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  label: string;
  value: number | string;
  color: "primary" | "success" | "info" | "warning";
}>();

const borderClass = computed(() => {
  return {
    primary: "border-[var(--sb-primary)]",
    success: "border-emerald-500",
    info: "border-cyan-500",
    warning: "border-amber-500"
  }[props.color];
});

const textClass = computed(() => {
  return {
    primary: "text-[var(--sb-primary)]",
    success: "text-emerald-600",
    info: "text-cyan-600",
    warning: "text-amber-600"
  }[props.color];
});
</script>
