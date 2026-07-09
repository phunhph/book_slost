<template>
  <div>
    <!-- Top toolbar & search -->
    <div class="mb-5 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
      <div class="min-w-0">
        <h1 class="text-xl font-bold text-white sm:text-2xl">{{ title }}</h1>
        <p v-if="subtitle" class="mt-1 text-sm text-slate-400">{{ subtitle }}</p>
      </div>
      <div class="flex w-full flex-col gap-2 sm:flex-row sm:items-center sm:justify-end lg:w-auto">
        <slot name="toolbar" />
        <div class="relative w-full sm:max-w-xs">
          <input
            v-model="query"
            type="search"
            :placeholder="searchPlaceholder"
            class="field"
            @input="page = 1"
          />
        </div>
      </div>
    </div>

    <!-- Filter Chips -->
    <div v-if="filters.length" class="mb-5 flex flex-wrap items-center gap-2">
      <button
        v-for="item in filters"
        :key="item.value"
        type="button"
        class="filter-chip"
        :class="activeFilter === item.value ? 'filter-chip--active' : ''"
        @click="setFilter(item.value)"
      >
        {{ item.label }}
        <span v-if="item.count != null" class="opacity-75">({{ item.count }})</span>
      </button>
    </div>

    <!-- Mobile view: Grid of Cards -->
    <div class="space-y-3 md:hidden">
      <article
        v-for="(row, index) in pagedRows"
        :key="`card-${page}-${index}`"
        class="rounded-2xl border border-white/10 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl"
      >
        <dl class="space-y-3.5">
          <div v-for="col in columns" :key="col.key">
            <dt class="text-[10px] font-bold uppercase tracking-wider text-slate-500">{{ col.label }}</dt>
            <dd class="mt-1 break-words text-sm text-slate-200">
              <slot :name="`cell-${col.key}`" :row="row">{{ formatValue(row[col.key]) }}</slot>
            </dd>
          </div>
        </dl>
      </article>
      <p
        v-if="filteredRows.length === 0"
        class="rounded-2xl border border-white/10 bg-slate-900/40 backdrop-blur-xl px-4 py-8 text-center text-slate-400 text-sm shadow-xl"
      >
        Không có dữ liệu
      </p>
    </div>

    <!-- Desktop view: Standard Table -->
    <div class="hidden overflow-hidden rounded-2xl border border-white/10 bg-slate-900/40 backdrop-blur-xl shadow-xl md:block">
      <div class="overflow-x-auto">
        <table class="min-w-full text-left text-sm">
          <thead class="bg-black/25 text-[10px] uppercase tracking-wider text-slate-400">
            <tr>
              <th v-for="col in columns" :key="col.key" class="px-5 py-3.5 font-bold">{{ col.label }}</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(row, index) in pagedRows" 
              :key="`${page}-${index}`" 
              class="border-t border-white/5 transition hover:bg-white/[0.02]"
            >
              <td v-for="col in columns" :key="col.key" class="max-w-[16rem] truncate px-5 py-3.5 text-slate-200">
                <slot :name="`cell-${col.key}`" :row="row">{{ formatValue(row[col.key]) }}</slot>
              </td>
            </tr>
            <tr v-if="filteredRows.length === 0">
              <td :colspan="columns.length" class="px-5 py-8 text-center text-slate-400 text-sm">Không có dữ liệu</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination bar -->
      <div
        v-if="filteredRows.length > 0"
        class="flex flex-col gap-3 border-t border-white/5 bg-black/15 px-5 py-3.5 sm:flex-row sm:items-center sm:justify-between"
      >
        <p class="text-xs text-slate-400">
          Hiển thị
          <span class="font-semibold text-white">{{ rangeStart }}–{{ rangeEnd }}</span>
          / {{ filteredRows.length }}
        </p>
        <div class="flex flex-wrap items-center gap-4">
          <label class="flex items-center gap-2 text-xs text-slate-400">
            <span>Mỗi trang</span>
            <select v-model.number="pageSize" class="page-size" @change="page = 1">
              <option v-for="size in pageSizes" :key="size" :value="size">{{ size }}</option>
            </select>
          </label>
          <div class="flex items-center gap-1.5">
            <button type="button" class="page-btn" :disabled="page <= 1" @click="page -= 1">Trước</button>
            <span class="px-2 text-xs font-semibold text-slate-300">{{ page }} / {{ totalPages }}</span>
            <button type="button" class="page-btn" :disabled="page >= totalPages" @click="page += 1">Sau</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile view pagination -->
    <div
      v-if="filteredRows.length > 0"
      class="mt-3 flex flex-col gap-3 rounded-2xl border border-white/10 bg-slate-900/40 backdrop-blur-xl px-4 py-3.5 shadow-xl md:hidden"
    >
      <p class="text-xs text-slate-400">
        Hiển thị
        <span class="font-semibold text-white">{{ rangeStart }}–{{ rangeEnd }}</span>
        / {{ filteredRows.length }}
      </p>
      <div class="flex flex-wrap items-center justify-between gap-2">
        <select v-model.number="pageSize" class="page-size" @change="page = 1">
          <option v-for="size in pageSizes" :key="size" :value="size">{{ size }}/trang</option>
        </select>
        <div class="flex items-center gap-1.5">
          <button type="button" class="page-btn" :disabled="page <= 1" @click="page -= 1">Trước</button>
          <span class="px-2 text-xs font-semibold text-slate-300">{{ page }} / {{ totalPages }}</span>
          <button type="button" class="page-btn" :disabled="page >= totalPages" @click="page += 1">Sau</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

type Column = { key: string; label: string };
type FilterOption = { value: string; label: string; count?: number };

const props = withDefaults(
  defineProps<{
    title: string;
    subtitle?: string;
    searchPlaceholder?: string;
    columns: Column[];
    rows: Record<string, unknown>[];
    searchKeys?: string[];
    filters?: FilterOption[];
    filterKey?: string;
    initialPageSize?: number;
  }>(),
  {
    searchPlaceholder: "Tìm kiếm...",
    filters: () => [],
    filterKey: "status",
    initialPageSize: 10,
  },
);

const query = ref("");
const activeFilter = ref("all");
const page = ref(1);
const pageSize = ref(props.initialPageSize);
const pageSizes = [10, 20, 50];

const filteredRows = computed(() => {
  let result = props.rows;
  if (activeFilter.value !== "all" && props.filterKey) {
    result = result.filter((row) => String(row[props.filterKey] ?? "") === activeFilter.value);
  }
  const q = query.value.trim().toLowerCase();
  if (!q) return result;
  const keys = props.searchKeys ?? props.columns.map((c) => c.key);
  return result.filter((row) => keys.some((key) => String(row[key] ?? "").toLowerCase().includes(q)));
});

const totalPages = computed(() => Math.max(1, Math.ceil(filteredRows.value.length / pageSize.value)));

const pagedRows = computed(() => {
  const start = (page.value - 1) * pageSize.value;
  return filteredRows.value.slice(start, start + pageSize.value);
});

const rangeStart = computed(() => (filteredRows.value.length === 0 ? 0 : (page.value - 1) * pageSize.value + 1));
const rangeEnd = computed(() => Math.min(page.value * pageSize.value, filteredRows.value.length));

watch(filteredRows, () => {
  if (page.value > totalPages.value) page.value = totalPages.value;
});

function setFilter(value: string) {
  activeFilter.value = value;
  page.value = 1;
}

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "-";
  return String(value);
}
</script>

<style scoped>
.filter-chip {
  @apply rounded-full border border-white/10 bg-white/5 px-3.5 py-1.5 text-xs font-semibold text-slate-300 transition hover:bg-white/10 hover:text-white cursor-pointer;
}
.filter-chip--active {
  @apply border-indigo-500/30 bg-gradient-to-r from-indigo-600 to-indigo-500 text-white shadow-lg shadow-indigo-500/20;
}
.page-btn {
  @apply h-9 rounded-xl border border-white/10 bg-white/5 px-3.5 text-xs font-semibold text-slate-300 transition hover:bg-white/10 hover:text-white disabled:cursor-not-allowed disabled:opacity-40 cursor-pointer;
}
.page-size {
  @apply h-9 rounded-xl border border-white/10 bg-black/25 px-2.5 text-xs text-white outline-none focus:border-indigo-500 transition cursor-pointer;
}
</style>
