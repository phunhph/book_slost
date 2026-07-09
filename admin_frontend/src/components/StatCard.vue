<template>
  <div class="rounded-2xl border border-white/10 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl relative overflow-hidden flex flex-col justify-between">
    <!-- Glowing background accent -->
    <div 
      class="absolute top-0 right-0 w-24 h-24 rounded-full blur-[45px] opacity-15"
      :class="bgAccentClass"
    />
    <!-- Accent indicator bar on the left -->
    <div class="absolute inset-y-0 left-0 w-1 rounded-r-full" :class="bgBarClass" />

    <div class="text-[10px] font-bold uppercase tracking-wider pl-2" :class="textClass">{{ label }}</div>
    <div class="mt-2 text-2xl font-bold text-white pl-2">{{ value }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  label: string;
  value: number | string;
  color: "primary" | "success" | "info" | "warning";
}>();

const bgBarClass = computed(() => {
  return {
    primary: "bg-indigo-500",
    success: "bg-emerald-500",
    info: "bg-cyan-500",
    warning: "bg-amber-500"
  }[props.color];
});

const bgAccentClass = computed(() => {
  return {
    primary: "bg-indigo-500",
    success: "bg-emerald-500",
    info: "bg-cyan-500",
    warning: "bg-amber-500"
  }[props.color];
});

const textClass = computed(() => {
  return {
    primary: "text-indigo-400",
    success: "text-emerald-400",
    info: "text-cyan-400",
    warning: "text-amber-400"
  }[props.color];
});
</script>
