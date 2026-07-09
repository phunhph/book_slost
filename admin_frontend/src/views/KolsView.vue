<template>
  <DataTable
    title="Danh sách KOL"
    subtitle="Tài khoản creator trên hệ thống"
    search-placeholder="Tìm tên, username, email..."
    :columns="columns"
    :rows="tableRows"
    :search-keys="['email', 'username', 'display_name']"
    :filters="statusFilters"
    filter-key="status_key"
  >
    <template #cell-is_active="{ row }">
      <span class="badge" :class="row.is_active ? 'badge-success' : 'badge-muted'">
        {{ row.is_active ? "Đang hoạt động" : "Ngưng" }}
      </span>
    </template>
    <template #cell-created_at="{ row }">
      {{ formatDate(String(row.created_at)) }}
    </template>
  </DataTable>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { fetchKols } from "@/api/auth";
import DataTable from "@/components/DataTable.vue";
import { useAuthStore } from "@/stores/auth";
import type { KolRow } from "@/types";

const auth = useAuthStore();
const rows = ref<KolRow[]>([]);
const columns = [
  { key: "display_name", label: "Tên hiển thị" },
  { key: "username", label: "Username" },
  { key: "email", label: "Email" },
  { key: "is_active", label: "Trạng thái" },
  { key: "created_at", label: "Ngày tạo" },
];

const tableRows = computed(() =>
  rows.value.map((row) => ({
    ...row,
    status_key: row.is_active ? "active" : "inactive",
  })) as unknown as Record<string, unknown>[],
);

const statusFilters = computed(() => {
  const active = rows.value.filter((row) => row.is_active).length;
  const inactive = rows.value.length - active;
  return [
    { value: "all", label: "Tất cả", count: rows.value.length },
    { value: "active", label: "Đang hoạt động", count: active },
    { value: "inactive", label: "Ngưng", count: inactive },
  ];
});

onMounted(async () => {
  if (!auth.token) return;
  rows.value = await fetchKols(auth.token);
});

function formatDate(value: string) {
  return new Date(value).toLocaleString("vi-VN");
}
</script>

<style scoped>
.badge {
  @apply rounded-full px-3 py-1 text-xs font-bold;
}
.badge-success {
  @apply bg-emerald-100 text-emerald-700;
}
.badge-muted {
  @apply bg-slate-100 text-slate-600;
}
</style>
