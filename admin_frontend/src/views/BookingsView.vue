<template>
  <DataTable
    title="Danh sách booking"
    subtitle="Quản lý toàn bộ lịch đặt trên hệ thống"
    search-placeholder="Tìm KOL, khách, SĐT..."
    :columns="columns"
    :rows="tableRows"
    :search-keys="['guest_name', 'guest_phone', 'kol_display_name', 'status', 'payment_code']"
    :filters="statusFilters"
    filter-key="status"
  >
    <template #cell-status="{ row }">
      <span class="badge" :class="statusClass(String(row.status))">{{ statusLabel(String(row.status)) }}</span>
    </template>
    <template #cell-scheduled_at="{ row }">
      {{ formatDate(String(row.scheduled_at)) }}
    </template>
    <template #cell-total_amount="{ row }">
      {{ formatMoney(Number(row.total_amount || 0), String(row.currency || "VND")) }}
    </template>
  </DataTable>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

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
  { key: "status", label: "Trạng thái" },
];

const tableRows = computed(() => rows.value as unknown as Record<string, unknown>[]);

const statusFilters = computed(() => {
  const counts = {
    pending: 0,
    confirmed: 0,
    completed: 0,
    cancelled: 0,
  };
  for (const row of rows.value) {
    if (row.status in counts) counts[row.status as keyof typeof counts] += 1;
  }
  return [
    { value: "all", label: "Tất cả", count: rows.value.length },
    { value: "pending", label: "Chờ xử lý", count: counts.pending },
    { value: "confirmed", label: "Đã xác nhận", count: counts.confirmed },
    { value: "completed", label: "Hoàn thành", count: counts.completed },
    { value: "cancelled", label: "Đã hủy", count: counts.cancelled },
  ];
});

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
  return (
    {
      pending: "Chờ xử lý",
      confirmed: "Đã xác nhận",
      completed: "Hoàn thành",
      cancelled: "Đã hủy",
    }[status] ?? status
  );
}

function statusClass(status: string) {
  return (
    {
      pending: "badge-warning",
      confirmed: "badge-info",
      completed: "badge-success",
      cancelled: "badge-muted",
    }[status] ?? "badge-muted"
  );
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
