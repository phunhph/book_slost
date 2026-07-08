<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import { redirectByRole, shouldRedirectAuthenticatedRole } from "@/lib/appUrls";
import { getErrorMessage } from "@/lib/errors";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const message = ref("Đang hoàn tất đăng nhập Google...");
const isError = ref(false);

onMounted(async () => {
  const accessToken = typeof route.query.access_token === "string" ? route.query.access_token : null;
  const error = typeof route.query.error === "string" ? route.query.error : null;

  if (error) {
    message.value = getErrorMessage(error, "Đăng nhập Google thất bại.");
    isError.value = true;
    return;
  }

  if (!accessToken) {
    message.value = "Thiếu access token từ Google callback.";
    isError.value = true;
    return;
  }

  try {
    await authStore.completeGoogleLogin(accessToken);
    if (authStore.user && shouldRedirectAuthenticatedRole(authStore.user.role, route.path)) {
      redirectByRole(authStore.user.role, authStore.accessToken);
      return;
    }
    message.value = "Đăng nhập Google thành công. Đang chuyển hướng...";
    window.setTimeout(() => {
      router.replace("/");
    }, 900);
  } catch (callbackError) {
    message.value = getErrorMessage(callbackError, "Đăng nhập Google thất bại.");
    isError.value = true;
  }
});
</script>

<template>
  <section class="mx-auto flex min-h-[calc(100vh-88px)] max-w-3xl items-center justify-center px-4 py-10 sm:px-6 lg:px-8">
    <div class="w-full rounded-[2rem] border border-white/10 bg-white/6 p-8 text-center">
      <p class="text-sm uppercase tracking-[0.28em]" :class="isError ? 'text-rose-200' : 'text-sky-300'">Google OAuth</p>
      <h1 class="mt-4 text-3xl font-semibold text-white">{{ isError ? 'Lỗi xác thực' : 'Đang đăng nhập' }}</h1>
      <p class="mt-4 text-base leading-7" :class="isError ? 'text-rose-100' : 'text-slate-300'">{{ message }}</p>
      <RouterLink to="/" class="mt-6 inline-flex rounded-full border border-white/12 px-5 py-3 text-sm font-medium text-white transition hover:bg-white/8">
        Về trang chủ
      </RouterLink>
    </div>
  </section>
</template>
