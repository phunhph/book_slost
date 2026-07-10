<template>
  <div>
    <DataTable
      title="Quản lý tài khoản"
      subtitle="Danh sách và quản trị toàn bộ tài khoản trên hệ thống"
      search-placeholder="Tìm tên, email, SĐT hoặc username..."
      :columns="columns"
      :rows="tableRows"
      :search-keys="['email', 'display_name', 'username', 'phone']"
      :filters="roleFilters"
      filter-key="role"
    >
      <!-- Toolbar Button to Add User -->
      <template #toolbar>
        <button
          type="button"
          class="btn-primary text-xs cursor-pointer active:scale-95"
          @click="openCreateModal"
        >
          + Thêm tài khoản
        </button>
      </template>

      <!-- Role Badge Column -->
      <template #cell-role="{ row }">
        <span class="badge" :class="roleClass(String(row.role))">
          {{ roleLabel(String(row.role)) }}
        </span>
      </template>

      <!-- Status Badge Column -->
      <template #cell-is_active="{ row }">
        <span class="badge" :class="row.is_active ? 'badge-success' : 'badge-muted'">
          {{ row.is_active ? "Đang hoạt động" : "Ngưng hoạt động" }}
        </span>
      </template>

      <!-- Date Formatter Column -->
      <template #cell-created_at="{ row }">
        {{ formatDate(String(row.created_at)) }}
      </template>

      <!-- Actions Column -->
      <template #cell-actions="{ row }">
        <div class="flex items-center gap-2">
          <button
            type="button"
            class="text-xs font-semibold px-2 py-1 bg-white/5 hover:bg-indigo-500/20 hover:text-indigo-400 rounded-lg transition cursor-pointer"
            @click="openEditModal(row)"
          >
            Sửa
          </button>
          <button
            type="button"
            class="text-xs font-semibold px-2 py-1 bg-white/5 hover:bg-rose-500/20 hover:text-rose-400 rounded-lg transition cursor-pointer"
            @click="confirmDelete(row)"
          >
            Xóa
          </button>
        </div>
      </template>
    </DataTable>

    <!-- User Modal Component -->
    <UserModal
      :show="showModal"
      :user="selectedUser"
      :saving="saving"
      @close="showModal = false"
      @save="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import { fetchUsers, createAdminUser, updateAdminUser, deleteAdminUser } from "@/api/auth";
import DataTable from "@/components/DataTable.vue";
import UserModal from "@/components/UserModal.vue";
import { useAuthStore } from "@/stores/auth";
import type { UserRow } from "@/types";

const auth = useAuthStore();
const rows = ref<UserRow[]>([]);
const showModal = ref(false);
const selectedUser = ref<UserRow | null>(null);
const saving = ref(false);

const columns = [
  { key: "display_name", label: "Tên" },
  { key: "email", label: "Email" },
  { key: "role", label: "Vai trò" },
  { key: "is_active", label: "Trạng thái" },
  { key: "created_at", label: "Ngày tạo" },
  { key: "actions", label: "Thao tác" },
];

const tableRows = computed(() => rows.value as unknown as Record<string, unknown>[]);

// Role Filters calculation
const roleFilters = computed(() => {
  const counts = {
    admin: 0,
    kol: 0,
    customer: 0,
  };
  for (const row of rows.value) {
    if (row.role in counts) counts[row.role as keyof typeof counts] += 1;
  }
  return [
    { value: "all", label: "Tất cả", count: rows.value.length },
    { value: "kol", label: "KOL", count: counts.kol },
    { value: "customer", label: "Khách hàng", count: counts.customer },
    { value: "admin", label: "Quản trị viên", count: counts.admin },
  ];
});

async function loadData() {
  if (!auth.token) return;
  try {
    rows.value = await fetchUsers(auth.token);
  } catch (error) {
    console.error("Failed to load users:", error);
    alert("Không tải được danh sách người dùng.");
  }
}

onMounted(loadData);

function openCreateModal() {
  selectedUser.value = null;
  showModal.value = true;
}

function openEditModal(row: any) {
  selectedUser.value = row as UserRow;
  showModal.value = true;
}

async function handleSave(payload: any) {
  if (!auth.token) return;
  saving.value = true;
  try {
    if (selectedUser.value) {
      // Edit mode
      await updateAdminUser(auth.token, selectedUser.value.id, payload);
    } else {
      // Create mode
      await createAdminUser(auth.token, payload);
    }
    showModal.value = false;
    await loadData();
  } catch (error: any) {
    console.error("Failed to save user:", error);
    alert(error.message || "Không lưu được tài khoản.");
  } finally {
    saving.value = false;
  }
}

async function confirmDelete(row: any) {
  const isKol = row.role === "kol";
  const warnMsg = isKol
    ? `CẢNH BÁO: Xóa tài khoản KOL "${row.display_name || row.email}" sẽ xóa toàn bộ bookings của KOL đó. Bạn có chắc chắn muốn xóa?`
    : `Bạn có chắc chắn muốn xóa tài khoản "${row.display_name || row.email}"?`;

  if (!confirm(warnMsg)) return;

  if (!auth.token) return;
  try {
    await deleteAdminUser(auth.token, row.id);
    await loadData();
  } catch (error: any) {
    console.error("Failed to delete user:", error);
    alert(error.message || "Xóa tài khoản thất bại.");
  }
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("vi-VN");
}

function roleLabel(role: string) {
  return (
    {
      admin: "Admin",
      kol: "KOL",
      customer: "Khách hàng",
    }[role] ?? role
  );
}

function roleClass(role: string) {
  return (
    {
      admin: "badge-admin",
      kol: "badge-kol",
      customer: "badge-customer",
    }[role] ?? "badge-muted"
  );
}
</script>

<style scoped>
.badge {
  @apply rounded-full px-3 py-1 text-xs font-bold uppercase;
}
.badge-admin {
  @apply bg-rose-500/20 text-rose-400 border border-rose-500/10;
}
.badge-kol {
  @apply bg-indigo-500/20 text-indigo-400 border border-indigo-500/10;
}
.badge-customer {
  @apply bg-emerald-500/20 text-emerald-400 border border-emerald-500/10;
}
.badge-success {
  @apply bg-emerald-100 text-emerald-700;
}
.badge-muted {
  @apply bg-slate-800 text-slate-400 border border-slate-700/50;
}
</style>
