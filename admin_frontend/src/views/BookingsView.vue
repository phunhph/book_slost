<template>
  <DataTable
    title="Danh sach booking"
    search-placeholder="Tim booking..."
    :columns="columns"
    :rows="rows"
    :search-keys="['guest_name', 'guest_phone', 'kol_display_name', 'status']"
  >
    <template #cell-status="{ row }">
      <span class="badge" :class="statusClass(String(row.status))">{{ row.status }}</span>
    </template>
    <template #cell-scheduled_at="{ row }">
      {{ formatDate(String(row.scheduled_at)) }}
    </template>
  </DataTable>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

import { fetchBookings } from "@/api/auth";
import DataTable from "@/components/DataTable.vue";
import { useAuthStore } from "@/stores/auth";
import type { BookingRow } from "@/types";

const auth = useAuthStore();
const rows = ref<BookingRow[]>([]);
const columns = [
  { key: "kol_display_name", label: "KOL" },
  { key: "guest_name", label: "Khach" },
  { key: "guest_phone", label: "SDT" },
  { key: "scheduled_at", label: "Thoi gian" },
  { key: "status", label: "Trang thai" }
];

onMounted(async () => {
  if (!auth.token) return;
  rows.value = await fetchBookings(auth.token);
});

function formatDate(value: string) {
  return new Date(value).toLocaleString("vi-VN");
}

function statusClass(status: string) {
  return {
    pending: "badge-warning",
    confirmed: "badge-info",
    completed: "badge-success",
    cancelled: "badge-muted"
  }[status] ?? "badge-muted";
}
</script>

<style scoped>
.badge {
  @apply rounded-full px-3 py-1 text-xs font-bold uppercase;
}
.badge-warning {
  @apply bg-amber-100 text-amber-700;
}
.badge-info {
  @apply bg-cyan-100 text-cyan-700;
}
.badge-success {
  @apply bg-emerald-100 text-emerald-700;
}
.badge-muted {
  @apply bg-slate-100 text-slate-600;
}
</style>
