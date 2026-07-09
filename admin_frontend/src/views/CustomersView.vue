<template>
  <DataTable
    title="Danh sách khách hàng"
    subtitle="Tài khoản khách đã đăng ký"
    search-placeholder="Tìm tên, email, SĐT..."
    :columns="columns"
    :rows="tableRows"
    :search-keys="['email', 'display_name', 'phone']"
  >
    <template #cell-created_at="{ row }">
      {{ formatDate(String(row.created_at)) }}
    </template>
  </DataTable>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { fetchCustomers } from "@/api/auth";
import DataTable from "@/components/DataTable.vue";
import { useAuthStore } from "@/stores/auth";
import type { CustomerRow } from "@/types";

const auth = useAuthStore();
const rows = ref<CustomerRow[]>([]);
const columns = [
  { key: "display_name", label: "Tên" },
  { key: "email", label: "Email" },
  { key: "phone", label: "SĐT" },
  { key: "created_at", label: "Ngày tạo" },
];

const tableRows = computed(() => rows.value as unknown as Record<string, unknown>[]);

onMounted(async () => {
  if (!auth.token) return;
  rows.value = await fetchCustomers(auth.token);
});

function formatDate(value: string) {
  return new Date(value).toLocaleString("vi-VN");
}
</script>
