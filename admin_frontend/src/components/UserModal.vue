<script setup lang="ts">
import { ref, watch } from "vue";
import type { UserRow, PlatformRow } from "@/types";
import { fetchAdminPlatforms } from "@/api/auth";
import { useAuthStore } from "@/stores/auth";

const props = defineProps<{
  show: boolean;
  user: UserRow | null;
  saving?: boolean;
}>();

const emit = defineEmits<{
  (e: "close"): void;
  (e: "save", data: any): void;
}>();

const auth = useAuthStore();
const email = ref("");
const password = ref("");
const role = ref("customer");
const isActive = ref(true);
const displayName = ref("");
const username = ref("");
const phone = ref("");
const contactLinks = ref<Array<{ platform: string; value: string; label?: string }>>([]);
const socialLinks = ref<Array<{ platform: string; url: string; label?: string }>>([]);

// Default fallback options in case API is slow
const contactOptions = ref([
  { value: "phone", label: "Điện thoại" },
  { value: "zalo", label: "Zalo" },
  { value: "messenger", label: "Facebook Messenger" },
  { value: "telegram", label: "Telegram" },
  { value: "viber", label: "Viber" },
]);

const socialOptions = ref([
  { value: "instagram", label: "Instagram" },
  { value: "tiktok", label: "TikTok" },
  { value: "facebook", label: "Facebook" },
  { value: "youtube", label: "YouTube" },
  { value: "twitter", label: "X / Twitter" },
  { value: "website", label: "Website" },
]);

async function loadPlatforms() {
  if (!auth.token) return;
  try {
    const list = await fetchAdminPlatforms(auth.token);
    // Filter active platforms
    const active = list.filter((p) => p.is_active);
    
    contactOptions.value = active
      .filter((p) => p.category === "contact")
      .map((p) => ({ value: p.key, label: p.label }));

    socialOptions.value = active
      .filter((p) => p.category === "social")
      .map((p) => ({ value: p.key, label: p.label }));
  } catch (error) {
    console.error("Failed to load platforms in modal:", error);
  }
}

watch(
  () => props.show,
  (newShow) => {
    if (newShow) {
      loadPlatforms();
      if (props.user) {
        email.value = props.user.email;
        password.value = "";
        role.value = props.user.role;
        isActive.value = props.user.is_active;
        displayName.value = props.user.display_name || "";
        username.value = props.user.username || "";
        phone.value = props.user.phone || "";
        contactLinks.value = props.user.contact_links
          ? JSON.parse(JSON.stringify(props.user.contact_links))
          : [];
        socialLinks.value = props.user.social_links
          ? JSON.parse(JSON.stringify(props.user.social_links))
          : [];
      } else {
        email.value = "";
        password.value = "";
        role.value = "customer";
        isActive.value = true;
        displayName.value = "";
        username.value = "";
        phone.value = "";
        contactLinks.value = [];
        socialLinks.value = [];
      }
    }
  }
);

function addLink() {
  const defaultPlat = contactOptions.value[0]?.value || "phone";
  contactLinks.value.push({ platform: defaultPlat, value: "", label: "" });
}

function removeLink(index: number) {
  contactLinks.value.splice(index, 1);
}

function addSocialLink() {
  const defaultPlat = socialOptions.value[0]?.value || "instagram";
  socialLinks.value.push({ platform: defaultPlat, url: "", label: "" });
}

function removeSocialLink(index: number) {
  socialLinks.value.splice(index, 1);
}

function handleSubmit() {
  const payload: any = {
    email: email.value.trim(),
    role: role.value,
    is_active: isActive.value,
    display_name: displayName.value.trim() || null,
    phone: phone.value.trim() || null,
    contact_links: contactLinks.value
      .map((link) => ({
        platform: link.platform,
        value: link.value.trim(),
        label: link.label?.trim() || null,
      }))
      .filter((link) => link.value !== ""),
    social_links: role.value === "kol" ? socialLinks.value
      .map((link) => ({
        platform: link.platform,
        url: link.url.trim(),
        label: link.label?.trim() || null,
      }))
      .filter((link) => link.url !== "") : [],
  };

  if (!props.user) {
    if (!password.value) {
      alert("Vui lòng nhập mật khẩu cho tài khoản mới.");
      return;
    }
    payload.password = password.value;
  } else {
    if (password.value) {
      payload.password = password.value;
    }
  }

  if (role.value === "kol") {
    if (!username.value.trim()) {
      alert("Tài khoản KOL yêu cầu nhập username.");
      return;
    }
    payload.username = username.value.trim();
  } else {
    payload.username = null;
  }

  emit("save", payload);
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Overlay -->
    <div class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm" @click="emit('close')" />

    <!-- Modal Content -->
    <div class="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto rounded-3xl border border-white/10 bg-slate-900/90 backdrop-blur-xl p-6 shadow-2xl z-10 scrollbar-thin">
      <div class="flex items-center justify-between border-b border-white/5 pb-4 mb-4">
        <h2 class="text-lg font-bold text-white">
          {{ user ? "Chỉnh sửa tài khoản" : "Thêm tài khoản mới" }}
        </h2>
        <button
          type="button"
          class="text-slate-400 hover:text-white text-sm cursor-pointer p-1"
          @click="emit('close')"
        >
          ✕
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div class="grid gap-4 md:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-xs font-semibold text-slate-400">Email</label>
            <input
              v-model="email"
              type="email"
              required
              class="field"
              placeholder="example@gmail.com"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-xs font-semibold text-slate-400">
              Mật khẩu {{ user ? "(Để trống nếu không đổi)" : "" }}
            </label>
            <input
              v-model="password"
              type="password"
              :required="!user"
              class="field"
              placeholder="••••••••"
              minlength="8"
            />
          </div>
        </div>

        <div class="grid gap-4 md:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-xs font-semibold text-slate-400">Vai trò (Role)</label>
            <select v-model="role" class="field">
              <option value="customer">Khách hàng (Customer)</option>
              <option value="kol">Người nổi tiếng (KOL)</option>
              <option value="admin">Quản trị viên (Admin)</option>
            </select>
          </div>

          <div>
            <label class="mb-1.5 block text-xs font-semibold text-slate-400">Tên hiển thị</label>
            <input
              v-model="displayName"
              type="text"
              class="field"
              placeholder="VD: Nguyễn Văn A"
            />
          </div>
        </div>

        <!-- Conditional Field: Username for KOL -->
        <div v-if="role === 'kol'">
          <label class="mb-1.5 block text-xs font-semibold text-slate-400">Username (Profile Link Handle)</label>
          <input
            v-model="username"
            type="text"
            required
            class="field"
            placeholder="VD: van_a_kol (Chỉ chữ cái, số, gạch dưới)"
            pattern="^[a-zA-Z0-9_]+$"
          />
        </div>

        <!-- Conditional Field: Base Phone for contact info fallback -->
        <div v-if="role === 'customer'">
          <label class="mb-1.5 block text-xs font-semibold text-slate-400">Số điện thoại</label>
          <input
            v-model="phone"
            type="text"
            class="field"
            placeholder="VD: 0901234567"
          />
        </div>

        <!-- Dynamic Contact Links Section -->
        <div class="border-t border-white/5 pt-4">
          <div class="flex items-center justify-between mb-3">
            <div>
              <p class="text-sm font-bold text-white">Liên kết liên hệ trực tiếp</p>
              <p class="text-xs text-slate-400 mt-0.5">Hiển thị ngay dưới phần hero trên trang công khai (Zalo, SĐT, Messenger...)</p>
            </div>
            <button
              type="button"
              class="btn-secondary !h-8 !py-0 px-3 flex items-center justify-center cursor-pointer text-xs"
              @click="addLink"
            >
              + Thêm liên hệ
            </button>
          </div>

          <div v-if="!contactLinks.length" class="rounded-2xl border border-dashed border-white/10 p-5 text-center text-xs text-slate-500">
            Chưa có liên kết liên hệ nào được thiết lập.
          </div>

          <div class="space-y-3">
            <div
              v-for="(link, index) in contactLinks"
              :key="index"
              class="flex flex-col gap-3 rounded-2xl border border-white/5 bg-black/10 p-3 md:flex-row md:items-center"
            >
              <div class="w-full md:w-1/4">
                <label class="mb-1 block text-[10px] text-slate-500 uppercase tracking-wider">Nền tảng</label>
                <select v-model="link.platform" class="field !h-9 !px-2.5">
                  <option v-for="opt in contactOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
              </div>

              <div class="w-full md:w-2/5">
                <label class="mb-1 block text-[10px] text-slate-500 uppercase tracking-wider">Giá trị / Liên kết</label>
                <input
                  v-model="link.value"
                  type="text"
                  required
                  class="field !h-9"
                  placeholder="Link liên kết hoặc SĐT/ID"
                />
              </div>

              <div class="w-full md:w-1/4">
                <label class="mb-1 block text-[10px] text-slate-500 uppercase tracking-wider">Nhãn tùy chọn</label>
                <input
                  v-model="link.label"
                  type="text"
                  class="field !h-9"
                  placeholder="VD: Zalo chính"
                />
              </div>

              <button
                type="button"
                class="mt-4 md:mt-3 px-3 py-1.5 text-xs text-rose-400 hover:text-rose-300 font-semibold cursor-pointer shrink-0"
                @click="removeLink(index)"
              >
                Xóa
              </button>
            </div>
          </div>
        </div>

        <!-- Dynamic Social Links Section (KOL only) -->
        <div v-if="role === 'kol'" class="border-t border-white/5 pt-4">
          <div class="flex items-center justify-between mb-3">
            <div>
              <p class="text-sm font-bold text-white">Mạng xã hội & liên kết</p>
              <p class="text-xs text-slate-400 mt-0.5">Liên kết đến Instagram, Tiktok, Youtube, Facebook, Website...</p>
            </div>
            <button
              type="button"
              class="btn-secondary !h-8 !py-0 px-3 flex items-center justify-center cursor-pointer text-xs"
              @click="addSocialLink"
            >
              + Thêm mạng xã hội
            </button>
          </div>

          <div v-if="!socialLinks.length" class="rounded-2xl border border-dashed border-white/10 p-5 text-center text-xs text-slate-500">
            Chưa có liên kết mạng xã hội nào được thiết lập.
          </div>

          <div class="space-y-3">
            <div
              v-for="(link, index) in socialLinks"
              :key="index"
              class="flex flex-col gap-3 rounded-2xl border border-white/5 bg-black/10 p-3 md:flex-row md:items-center"
            >
              <div class="w-full md:w-1/4">
                <label class="mb-1 block text-[10px] text-slate-500 uppercase tracking-wider">Nền tảng</label>
                <select v-model="link.platform" class="field !h-9 !px-2.5">
                  <option v-for="opt in socialOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
              </div>

              <div class="w-full md:w-2/5">
                <label class="mb-1 block text-[10px] text-slate-500 uppercase tracking-wider">Đường dẫn URL</label>
                <input
                  v-model="link.url"
                  type="url"
                  required
                  class="field !h-9"
                  placeholder="https://..."
                />
              </div>

              <div class="w-full md:w-1/4">
                <label class="mb-1 block text-[10px] text-slate-500 uppercase tracking-wider">Nhãn hiển thị</label>
                <input
                  v-model="link.label"
                  type="text"
                  class="field !h-9"
                  placeholder="VD: Instagram chính"
                />
              </div>

              <button
                type="button"
                class="mt-4 md:mt-3 px-3 py-1.5 text-xs text-rose-400 hover:text-rose-300 font-semibold cursor-pointer shrink-0"
                @click="removeSocialLink(index)"
              >
                Xóa
              </button>
            </div>
          </div>
        </div>

        <!-- Account Status Toggle -->
        <div class="flex items-center gap-3 border-t border-white/5 pt-4">
          <input
            v-model="isActive"
            type="checkbox"
            id="is_active_toggle"
            class="h-4 w-4 rounded border-white/10 bg-black/20 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
          />
          <label for="is_active_toggle" class="text-sm font-semibold text-slate-300 cursor-pointer">
            Kích hoạt tài khoản (Cho phép đăng nhập và hoạt động)
          </label>
        </div>

        <!-- Footer Actions -->
        <div class="flex items-center justify-end gap-3 border-t border-white/5 pt-4 mt-6">
          <button
            type="button"
            class="btn-secondary"
            :disabled="saving"
            @click="emit('close')"
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
</template>

<style scoped>
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
