<template>
  <DataTable title="Danh sách KOL" search-placeholder="Tìm KOL..." :columns="columns" :rows="rows" :search-keys="['email', 'username', 'display_name']">
    <template #cell-is_active="{ row }">
      <span class="badge" :class="row.is_active ? 'badge-success' : 'badge-muted'">{{ row.is_active ? "Đang hoạt động" : "Ngưng" }}</span>
    </template>
  </DataTable>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

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
  { key: "created_at", label: "Ngày tạo" }
];

onMounted(async () => {
  if (!auth.token) return;
  rows.value = await fetchKols(auth.token);
});
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
