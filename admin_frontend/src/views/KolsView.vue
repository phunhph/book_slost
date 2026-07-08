<template>
  <DataTable title="Danh sach KOL" search-placeholder="Tim KOL..." :columns="columns" :rows="rows" :search-keys="['email', 'username', 'display_name']">
    <template #cell-is_active="{ row }">
      <span class="badge" :class="row.is_active ? 'badge-success' : 'badge-muted'">{{ row.is_active ? "Active" : "Inactive" }}</span>
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
  { key: "display_name", label: "Ten hien thi" },
  { key: "username", label: "Username" },
  { key: "email", label: "Email" },
  { key: "is_active", label: "Trang thai" },
  { key: "created_at", label: "Ngay tao" }
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
