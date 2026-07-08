<template>
  <div>
    <div class="mb-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
      <div class="min-w-0">
        <h1 class="text-xl font-bold text-slate-800 sm:text-2xl">{{ title }}</h1>
        <p v-if="subtitle" class="mt-1 text-sm text-slate-500">{{ subtitle }}</p>
      </div>
      <div class="flex w-full flex-col gap-2 sm:flex-row sm:items-center sm:justify-end lg:w-auto">
        <slot name="toolbar" />
        <div class="relative w-full sm:max-w-xs">
          <input
            v-model="query"
            type="search"
            :placeholder="searchPlaceholder"
            class="search"
            @input="page = 1"
          />
        </div>
      </div>
    </div>

    <div v-if="filters.length" class="mb-4 flex flex-wrap items-center gap-2">
      <button
        v-for="item in filters"
        :key="item.value"
        type="button"
        class="filter-chip"
        :class="activeFilter === item.value ? 'filter-chip--active' : ''"
        @click="setFilter(item.value)"
      >
        {{ item.label }}
        <span v-if="item.count != null" class="opacity-70">({{ item.count }})</span>
      </button>
    </div>

    <div class="space-y-3 md:hidden">
      <article
        v-for="(row, index) in pagedRows"
        :key="`card-${page}-${index}`"
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
      <p
        v-if="filteredRows.length === 0"
        class="rounded-xl border border-[var(--sb-card-border)] bg-white px-4 py-8 text-center text-slate-500 card-shadow"
      >
        Không có dữ liệu
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
            <tr v-for="(row, index) in pagedRows" :key="`${page}-${index}`" class="border-t border-slate-100">
              <td v-for="col in columns" :key="col.key" class="max-w-[16rem] truncate px-4 py-3 text-slate-700">
                <slot :name="`cell-${col.key}`" :row="row">{{ formatValue(row[col.key]) }}</slot>
              </td>
            </tr>
            <tr v-if="filteredRows.length === 0">
              <td :colspan="columns.length" class="px-4 py-8 text-center text-slate-500">Không có dữ liệu</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div
        v-if="filteredRows.length > 0"
        class="flex flex-col gap-3 border-t border-slate-100 bg-slate-50/80 px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
      >
        <p class="text-sm text-slate-500">
          Hiển thị
          <span class="font-semibold text-slate-700">{{ rangeStart }}–{{ rangeEnd }}</span>
          / {{ filteredRows.length }}
        </p>
        <div class="flex flex-wrap items-center gap-2">
          <label class="flex items-center gap-2 text-sm text-slate-500">
            <span>Mỗi trang</span>
            <select v-model.number="pageSize" class="page-size" @change="page = 1">
              <option v-for="size in pageSizes" :key="size" :value="size">{{ size }}</option>
            </select>
          </label>
          <div class="flex items-center gap-1">
            <button type="button" class="page-btn" :disabled="page <= 1" @click="page -= 1">Trước</button>
            <span class="px-2 text-sm font-medium text-slate-600">{{ page }} / {{ totalPages }}</span>
            <button type="button" class="page-btn" :disabled="page >= totalPages" @click="page += 1">Sau</button>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="filteredRows.length > 0"
      class="mt-3 flex flex-col gap-3 rounded-xl border border-[var(--sb-card-border)] bg-white px-4 py-3 card-shadow md:hidden"
    >
      <p class="text-sm text-slate-500">
        Hiển thị
        <span class="font-semibold text-slate-700">{{ rangeStart }}–{{ rangeEnd }}</span>
        / {{ filteredRows.length }}
      </p>
      <div class="flex flex-wrap items-center justify-between gap-2">
        <select v-model.number="pageSize" class="page-size" @change="page = 1">
          <option v-for="size in pageSizes" :key="size" :value="size">{{ size }}/trang</option>
        </select>
        <div class="flex items-center gap-1">
          <button type="button" class="page-btn" :disabled="page <= 1" @click="page -= 1">Trước</button>
          <span class="px-2 text-sm font-medium text-slate-600">{{ page }} / {{ totalPages }}</span>
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
.search {
  @apply h-10 w-full rounded-lg border border-slate-200 bg-white px-4 text-sm outline-none focus:border-[var(--sb-primary)] focus:ring-2 focus:ring-blue-100;
}
.filter-chip {
  @apply rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:border-slate-300;
}
.filter-chip--active {
  @apply border-[var(--sb-primary)] bg-[var(--sb-primary)] text-white;
}
.page-btn {
  @apply h-9 rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40;
}
.page-size {
  @apply h-9 rounded-lg border border-slate-200 bg-white px-2 text-sm text-slate-700 outline-none focus:border-[var(--sb-primary)];
}
</style>
