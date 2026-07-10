<template>
  <div>
    <DataTable
      title="Cấu hình Nền tảng liên kết"
      subtitle="Quản lý danh sách các nền tảng liên hệ và mạng xã hội được hiển thị trên hệ thống"
      search-placeholder="Tìm kiếm nền tảng..."
      :columns="columns"
      :rows="tableRows"
      :search-keys="['key', 'label']"
      :filters="categoryFilters"
      filter-key="category"
    >
      <!-- Toolbar Button to Add Platform -->
      <template #toolbar>
        <button
          type="button"
          class="btn-primary text-xs cursor-pointer active:scale-95"
          @click="openCreateModal"
        >
          + Thêm nền tảng
        </button>
      </template>

      <!-- Label & Icon Column -->
      <template #cell-label="{ row }">
        <div class="flex items-center gap-2">
          <span class="text-base leading-none">{{ getPlatformEmoji(String(row.key)) }}</span>
          <span class="font-medium text-white">{{ row.label }}</span>
        </div>
      </template>

      <!-- Category Column -->
      <template #cell-category="{ row }">
        <span class="badge" :class="row.category === 'contact' ? 'badge-contact' : 'badge-social'">
          {{ row.category === 'contact' ? 'Liên hệ trực tiếp' : 'Mạng xã hội' }}
        </span>
      </template>

      <!-- Status Column -->
      <template #cell-is_active="{ row }">
        <span class="badge" :class="row.is_active ? 'badge-success' : 'badge-muted'">
          {{ row.is_active ? "Đang hoạt động" : "Ngưng hoạt động" }}
        </span>
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

    <!-- Platform Edit/Create Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm" @click="showModal = false" />

      <div class="relative w-full max-w-md rounded-3xl border border-white/10 bg-slate-900/90 backdrop-blur-xl p-6 shadow-2xl z-10 animate-fade-in">
        <div class="flex items-center justify-between border-b border-white/5 pb-4 mb-4">
          <h2 class="text-lg font-bold text-white">
            {{ selectedPlatform ? "Chỉnh sửa Nền tảng" : "Thêm Nền tảng mới" }}
          </h2>
          <button
            type="button"
            class="text-slate-400 hover:text-white text-sm cursor-pointer p-1"
            @click="showModal = false"
          >
            ✕
          </button>
        </div>

        <form @submit.prevent="handleSave" class="space-y-4">
          <div>
            <label class="mb-1.5 block text-xs font-semibold text-slate-400">Mã định danh (Key / Slug)</label>
            <input
              v-model="key"
              type="text"
              required
              class="field"
              placeholder="VD: threads (Chữ thường, không cách, không dấu)"
              pattern="^[a-z0-9_]+$"
              :disabled="!!selectedPlatform"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-xs font-semibold text-slate-400">Tên nền tảng (Label)</label>
            <input
              v-model="label"
              type="text"
              required
              class="field"
              placeholder="VD: Threads"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-xs font-semibold text-slate-400">Phân loại (Category)</label>
            <select v-model="category" class="field">
              <option value="contact">Liên hệ trực tiếp (Phone, Zalo...)</option>
              <option value="social">Mạng xã hội & liên kết (Facebook, Youtube, Website...)</option>
            </select>
          </div>

          <div class="flex items-center gap-3 pt-2">
            <input
              v-model="isActive"
              type="checkbox"
              id="platform_active"
              class="h-4 w-4 rounded border-white/10 bg-black/20 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
            />
            <label for="platform_active" class="text-sm font-semibold text-slate-300 cursor-pointer">
              Đang hoạt động (Kích hoạt cho người dùng lựa chọn)
            </label>
          </div>

          <div class="flex items-center justify-end gap-3 border-t border-white/5 pt-4 mt-6">
            <button
              type="button"
              class="btn-secondary"
              :disabled="saving"
              @click="showModal = false"
            >
              Hủy
            </button>
            <button type="submit" class="btn-primary min-w-[6rem]" :disabled="saving">
              {{ saving ? "Đang lưu..." : "Lưu lại" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { fetchAdminPlatforms, createAdminPlatform, updateAdminPlatform, deleteAdminPlatform } from "@/api/auth";
import DataTable from "@/components/DataTable.vue";
import { useAuthStore } from "@/stores/auth";
import type { PlatformRow } from "@/types";

const auth = useAuthStore();
const rows = ref<PlatformRow[]>([]);
const showModal = ref(false);
const selectedPlatform = ref<PlatformRow | null>(null);
const saving = ref(false);

const key = ref("");
const label = ref("");
const category = ref<"contact" | "social">("social");
const isActive = ref(true);

const columns = [
  { key: "key", label: "Mã nền tảng (Key)" },
  { key: "label", label: "Tên hiển thị" },
  { key: "category", label: "Phân loại" },
  { key: "is_active", label: "Trạng thái" },
  { key: "actions", label: "Thao tác" },
];

const categoryFilters = [
  { value: "", label: "Tất cả" },
  { value: "contact", label: "Liên hệ trực tiếp" },
  { value: "social", label: "Mạng xã hội" },
];

const tableRows = computed(() => rows.value as unknown as Record<string, unknown>[]);

async function loadData() {
  if (!auth.token) return;
  try {
    const list = await fetchAdminPlatforms(auth.token);
    rows.value = list;
  } catch (error) {
    console.error("Failed to load platforms:", error);
  }
}

onMounted(() => {
  loadData();
});

function openCreateModal() {
  selectedPlatform.value = null;
  key.value = "";
  label.value = "";
  category.value = "social";
  isActive.value = true;
  showModal.value = true;
}

function openEditModal(row: any) {
  const p = row as PlatformRow;
  selectedPlatform.value = p;
  key.value = p.key;
  label.value = p.label;
  category.value = p.category;
  isActive.value = p.is_active;
  showModal.value = true;
}

async function handleSave() {
  if (!auth.token) return;
  saving.value = true;
  try {
    const payload = {
      key: key.value.trim().toLowerCase(),
      label: label.value.trim(),
      category: category.value,
      is_active: isActive.value,
    };

    if (selectedPlatform.value) {
      await updateAdminPlatform(auth.token, selectedPlatform.value.id, payload);
    } else {
      await createAdminPlatform(auth.token, payload);
    }
    showModal.value = false;
    await loadData();
  } catch (error: any) {
    alert(error.message || "Lỗi lưu cấu hình nền tảng.");
  } finally {
    saving.value = false;
  }
}

async function confirmDelete(row: any) {
  const p = row as PlatformRow;
  if (!confirm(`Bạn có chắc chắn muốn xóa nền tảng "${p.label}" không?`)) {
    return;
  }
  if (!auth.token) return;
  try {
    await deleteAdminPlatform(auth.token, p.id);
    await loadData();
  } catch (error: any) {
    alert(error.message || "Lỗi xóa nền tảng.");
  }
}

function getPlatformEmoji(key: string): string {
  switch (key.toLowerCase()) {
    case "phone": return "📞";
    case "zalo": return "🔵";
    case "messenger": return "💬";
    case "telegram": return "✈️";
    case "viber": return "💜";
    case "instagram": return "📸";
    case "tiktok": return "🎵";
    case "youtube": return "🎥";
    case "shopee": return "🛍️";
    case "website": return "🌐";
    case "twitter": return "🐦";
    default: return "🔗";
  }
}
</script>

<style scoped>
.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
}
.badge-contact {
  background-color: rgba(56, 189, 248, 0.1); /* sky */
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.2);
}
.badge-social {
  background-color: rgba(168, 85, 247, 0.1); /* purple */
  color: #c084fc;
  border: 1px solid rgba(168, 85, 247, 0.2);
}
.badge-success {
  background-color: rgba(16, 185, 129, 0.1); /* emerald */
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.2);
}
.badge-muted {
  background-color: rgba(100, 116, 139, 0.1); /* slate */
  color: #94a3b8;
  border: 1px solid rgba(100, 116, 139, 0.2);
}
</style>
