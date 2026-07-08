<template>
  <div>
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h1 class="text-xl font-bold text-slate-800 sm:text-2xl">{{ title }}</h1>
      <input v-model="query" type="search" :placeholder="searchPlaceholder" class="search" />
    </div>

    <div class="space-y-3 md:hidden">
      <article
        v-for="(row, index) in filteredRows"
        :key="`card-${index}`"
        class="rounded-xl border border-[var(--sb-card-border)] bg-white p-4 card-shadow"
      >
        <dl class="space-y-3">
          <div v-for="col in columns" :key="col.key">
            <dt class="text-xs font-bold uppercase tracking-wider text-slate-500">{{ col.label }}</dt>
            <dd class="mt-1 break-words text-sm text-slate-700">
              <slot :name="`cell-${col.key}`" :row="row">{{ formatValue(row[col.key]) }}</slot>
            </dd>
          </div>
        </dl>
      </article>
      <p v-if="filteredRows.length === 0" class="rounded-xl border border-[var(--sb-card-border)] bg-white px-4 py-8 text-center text-slate-500 card-shadow">
        Khong co du lieu
      </p>
    </div>

    <div class="hidden overflow-hidden rounded-xl border border-[var(--sb-card-border)] bg-white card-shadow md:block">
      <div class="overflow-x-auto">
        <table class="min-w-full text-left text-sm">
          <thead class="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
            <tr>
              <th v-for="col in columns" :key="col.key" class="px-4 py-3 font-bold">{{ col.label }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in filteredRows" :key="index" class="border-t border-slate-100">
              <td v-for="col in columns" :key="col.key" class="max-w-[16rem] truncate px-4 py-3 text-slate-700">
                <slot :name="`cell-${col.key}`" :row="row">{{ formatValue(row[col.key]) }}</slot>
              </td>
            </tr>
            <tr v-if="filteredRows.length === 0">
              <td :colspan="columns.length" class="px-4 py-8 text-center text-slate-500">Khong co du lieu</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

type Column = { key: string; label: string };

const props = defineProps<{
  title: string;
  searchPlaceholder?: string;
  columns: Column[];
  rows: Record<string, unknown>[];
  searchKeys?: string[];
}>();

const query = ref("");

const filteredRows = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return props.rows;
  const keys = props.searchKeys ?? props.columns.map((c) => c.key);
  return props.rows.filter((row) => keys.some((key) => String(row[key] ?? "").toLowerCase().includes(q)));
});

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "-";
  return String(value);
}
</script>

<style scoped>
.search {
  @apply h-10 w-full rounded-lg border border-slate-200 px-4 text-sm outline-none focus:border-[var(--sb-primary)] sm:max-w-xs;
}
</style>
