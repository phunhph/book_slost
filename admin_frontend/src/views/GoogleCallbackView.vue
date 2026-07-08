<template>
  <div class="flex min-h-screen items-center justify-center p-6">
    <div class="w-full max-w-md rounded-2xl bg-white p-8 text-center card-shadow">
      <div class="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-2 border-slate-200 border-t-[var(--sb-primary)]" />
      <p class="text-sm text-slate-600">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { fetchMe } from "@/api/auth";
import { getErrorMessage } from "@/lib/errors";
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const message = ref("Đang xử lý đăng nhập Google...");

onMounted(async () => {
  const error = route.query.error as string | undefined;
  const accessToken = route.query.access_token as string | undefined;

  if (error) {
    message.value = getErrorMessage(error, "Đăng nhập Google thất bại.");
    return;
  }
  if (!accessToken) {
    message.value = "Không nhận được token từ Google.";
    return;
  }

  try {
    const user = await fetchMe(accessToken);
    if (user.role !== "admin") {
      message.value = "Tài khoản không có quyền admin.";
      return;
    }
    auth.acceptOAuthToken(accessToken);
    auth.user = user;
    router.replace("/dashboard");
  } catch (err) {
    message.value = getErrorMessage(err, "Đăng nhập Google thất bại.");
  }
});
</script>
