<template>
  <DataTable
    title="Danh sách booking"
    search-placeholder="Tìm booking..."
    :columns="columns"
    :rows="rows"
    :search-keys="['guest_name', 'guest_phone', 'kol_display_name', 'status']"
  >
    <template #cell-status="{ row }">
      <span class="badge" :class="statusClass(String(row.status))">{{ statusLabel(String(row.status)) }}</span>
    </template>
    <template #cell-scheduled_at="{ row }">
      {{ formatDate(String(row.scheduled_at)) }}
    </template>
    <template #cell-total_amount="{ row }">
      {{ formatMoney(Number(row.total_amount || 0), String(row.currency || 'VND')) }}
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
  { key: "guest_name", label: "Khách" },
  { key: "guest_phone", label: "SĐT" },
  { key: "scheduled_at", label: "Thời gian" },
  { key: "total_amount", label: "Số tiền" },
  { key: "payment_code", label: "Mã QR" },
  { key: "status", label: "Trạng thái" }
];

onMounted(async () => {
  if (!auth.token) return;
  rows.value = await fetchBookings(auth.token);
});

function formatDate(value: string) {
  return new Date(value).toLocaleString("vi-VN");
}

function formatMoney(amount: number, currency: string) {
  return `${new Intl.NumberFormat("vi-VN").format(amount)} ${currency}`;
}

function statusLabel(status: string) {
  return {
    pending: "Chờ xử lý",
    confirmed: "Đã xác nhận",
    completed: "Hoàn thành",
    cancelled: "Đã hủy"
  }[status] ?? status;
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
