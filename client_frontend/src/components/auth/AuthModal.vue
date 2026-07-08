<script setup lang="ts">
import { computed, onUnmounted, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";

import { getGoogleOAuthUrl } from "@/services/auth";
import { redirectByRole, shouldRedirectAuthenticatedRole } from "@/lib/appUrls";
import { getErrorMessage } from "@/lib/errors";
import { useAuthStore } from "@/stores/auth";
import { useToastStore } from "@/stores/toast";

type AuthMode = "login" | "register";
type FieldName = "displayName" | "username" | "email" | "password";

const props = defineProps<{
  isOpen: boolean;
  initialMode: AuthMode;
}>();

const emit = defineEmits<{
  close: [];
  authenticated: [];
}>();

const authStore = useAuthStore();
const toast = useToastStore();
const route = useRoute();
const mode = ref<AuthMode>(props.initialMode);
const email = ref("");
const password = ref("");
const displayName = ref("");
const username = ref("");
const isSubmitting = ref(false);
const fieldErrors = reactive<Partial<Record<FieldName, string>>>({});
const touched = reactive<Partial<Record<FieldName, boolean>>>({});

const googleUrl = computed(() => getGoogleOAuthUrl());

watch(
  () => props.initialMode,
  (value) => {
    mode.value = value;
  },
);

watch(
  () => props.isOpen,
  (open) => {
    document.body.style.overflow = open ? "hidden" : "";
    if (open) {
      Object.keys(fieldErrors).forEach((key) => delete fieldErrors[key as FieldName]);
      Object.keys(touched).forEach((key) => delete touched[key as FieldName]);
    }
  },
  { immediate: true },
);

onUnmounted(() => {
  document.body.style.overflow = "";
});

function inputClass(field: FieldName) {
  return [
    "w-full rounded-2xl border bg-white/5 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-500 focus:border-sky-400",
    touched[field] && fieldErrors[field] ? "border-rose-400/70" : "border-white/12",
  ];
}

function validateField(field: FieldName): string {
  let message = "";

  if (field === "email") {
    const value = email.value.trim();
    if (!value) message = "Vui lòng nhập email.";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) message = "Email không hợp lệ.";
  }

  if (field === "password") {
    if (!password.value) message = "Vui lòng nhập mật khẩu.";
    else if (password.value.length < 8) message = "Mật khẩu tối thiểu 8 ký tự.";
  }

  if (mode.value === "register") {
    if (field === "displayName" && !displayName.value.trim()) {
      message = "Vui lòng nhập tên hiển thị.";
    }
    if (field === "username") {
      const value = username.value.trim();
      if (value && !/^[a-zA-Z0-9._-]{3,}$/.test(value)) {
        message = "Username tối thiểu 3 ký tự (chữ, số, . _ -).";
      }
    }
  }

  if (message) fieldErrors[field] = message;
  else delete fieldErrors[field];
  return message;
}

function markTouched(field: FieldName) {
  touched[field] = true;
  validateField(field);
}

function validateForm(): boolean {
  const fields: FieldName[] =
    mode.value === "register"
      ? ["displayName", "username", "email", "password"]
      : ["email", "password"];
  let ok = true;
  for (const field of fields) {
    touched[field] = true;
    if (validateField(field)) ok = false;
  }
  return ok;
}

async function submit() {
  if (!validateForm()) {
    toast.error("Vui lòng sửa các ô đang báo lỗi.");
    return;
  }

  isSubmitting.value = true;

  try {
    if (mode.value === "login") {
      const response = await authStore.login({
        email: email.value.trim(),
        password: password.value,
      });
      if (authStore.user && shouldRedirectAuthenticatedRole(authStore.user.role, route.path)) {
        redirectByRole(authStore.user.role, authStore.accessToken);
        return;
      }
      toast.success(response.message);
    } else {
      const response = await authStore.register({
        email: email.value.trim(),
        password: password.value,
        display_name: displayName.value.trim() || undefined,
        username: username.value.trim() || undefined,
      });
      if (authStore.user && shouldRedirectAuthenticatedRole(authStore.user.role, route.path)) {
        redirectByRole(authStore.user.role, authStore.accessToken);
        return;
      }
      toast.success(response.message);
    }

    emit("authenticated");
  } catch (error) {
    toast.error(getErrorMessage(error, "Xác thực thất bại."));
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-slate-950/70 px-4 py-6 backdrop-blur-sm sm:items-center sm:py-10"
      role="dialog"
      aria-modal="true"
      @click.self="emit('close')"
    >
      <div class="my-auto w-full max-w-md max-h-[min(90dvh,calc(100vh-3rem))] overflow-y-auto rounded-[2rem] border border-white/12 bg-slate-950 p-5 shadow-2xl shadow-sky-950/40 sm:p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm uppercase tracking-[0.3em] text-sky-300">Khách hàng</p>
            <h2 class="mt-2 text-2xl font-semibold text-white">{{ mode === 'login' ? 'Chào mừng trở lại' : 'Tạo tài khoản' }}</h2>
          </div>
          <button class="rounded-full border border-white/10 px-3 py-2 text-sm text-slate-300 hover:bg-white/6" type="button" @click="emit('close')">Đóng</button>
        </div>

        <div class="mt-6 flex rounded-full border border-white/10 bg-white/5 p-1">
          <button
            class="flex-1 rounded-full px-4 py-2 text-sm font-medium transition"
            :class="mode === 'login' ? 'bg-white text-slate-900' : 'text-slate-300'"
            type="button"
            @click="mode = 'login'"
          >
            Đăng nhập
          </button>
          <button
            class="flex-1 rounded-full px-4 py-2 text-sm font-medium transition"
            :class="mode === 'register' ? 'bg-white text-slate-900' : 'text-slate-300'"
            type="button"
            @click="mode = 'register'"
          >
            Đăng ký
          </button>
        </div>

        <form class="mt-6 space-y-4" novalidate @submit.prevent="submit">
          <div v-if="mode === 'register'" class="grid gap-4 sm:grid-cols-2">
            <label class="block text-sm text-slate-200">
              <span class="mb-2 block">Tên hiển thị *</span>
              <input
                v-model="displayName"
                :class="inputClass('displayName')"
                placeholder="Nguyễn An"
                type="text"
                @blur="markTouched('displayName')"
                @input="validateField('displayName')"
              />
              <span v-if="touched.displayName && fieldErrors.displayName" class="mt-2 block text-xs text-rose-300">
                {{ fieldErrors.displayName }}
              </span>
            </label>
            <label class="block text-sm text-slate-200">
              <span class="mb-2 block">Username</span>
              <input
                v-model="username"
                :class="inputClass('username')"
                placeholder="nguyenan"
                type="text"
                @blur="markTouched('username')"
                @input="validateField('username')"
              />
              <span v-if="touched.username && fieldErrors.username" class="mt-2 block text-xs text-rose-300">
                {{ fieldErrors.username }}
              </span>
            </label>
          </div>

          <label class="block text-sm text-slate-200">
            <span class="mb-2 block">Email *</span>
            <input
              v-model="email"
              :class="inputClass('email')"
              placeholder="ban@example.com"
              type="email"
              @blur="markTouched('email')"
              @input="validateField('email')"
            />
            <span v-if="touched.email && fieldErrors.email" class="mt-2 block text-xs text-rose-300">
              {{ fieldErrors.email }}
            </span>
          </label>

          <label class="block text-sm text-slate-200">
            <span class="mb-2 block">Mật khẩu *</span>
            <input
              v-model="password"
              :class="inputClass('password')"
              placeholder="Tối thiểu 8 ký tự"
              type="password"
              @blur="markTouched('password')"
              @input="validateField('password')"
            />
            <span v-if="touched.password && fieldErrors.password" class="mt-2 block text-xs text-rose-300">
              {{ fieldErrors.password }}
            </span>
          </label>

          <button class="w-full rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? 'Vui lòng chờ...' : mode === 'login' ? 'Đăng nhập' : 'Tạo tài khoản' }}
          </button>
        </form>

        <div class="my-6 flex items-center gap-4 text-xs uppercase tracking-[0.24em] text-slate-500">
          <span class="h-px flex-1 bg-white/10"></span>
          <span>hoặc tiếp tục với</span>
          <span class="h-px flex-1 bg-white/10"></span>
        </div>

        <a :href="googleUrl" class="flex items-center justify-center rounded-2xl border border-white/12 px-4 py-3 text-sm font-medium text-white transition hover:border-white/25 hover:bg-white/6">
          Google
        </a>
      </div>
    </div>
  </Teleport>
</template>
