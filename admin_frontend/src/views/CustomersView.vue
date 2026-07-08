<template>
  <DataTable title="Danh sach khach hang" search-placeholder="Tim khach hang..." :columns="columns" :rows="rows" :search-keys="['email', 'display_name', 'phone']" />
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
  { key: "display_name", label: "Ten" },
  { key: "email", label: "Email" },
  { key: "phone", label: "SDT" },
  { key: "created_at", label: "Ngay tao" }
];

onMounted(async () => {
  if (!auth.token) return;
  rows.value = await fetchCustomers(auth.token);
});
</script>
