<template>
  <DataTable
    title="Danh sách khách hàng"
    search-placeholder="Tìm khách hàng..."
    :columns="columns"
    :rows="rows"
    :search-keys="['email', 'display_name', 'phone']"
  />
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

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
  { key: "created_at", label: "Ngày tạo" }
];

onMounted(async () => {
  if (!auth.token) return;
  rows.value = await fetchCustomers(auth.token);
});
</script>
