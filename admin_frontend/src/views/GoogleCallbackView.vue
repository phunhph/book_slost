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
import { useAuthStore } from "@/stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const message = ref("Dang xu ly dang nhap Google...");

onMounted(async () => {
  const error = route.query.error as string | undefined;
  const accessToken = route.query.access_token as string | undefined;

  if (error) {
    message.value = error;
    return;
  }
  if (!accessToken) {
    message.value = "Khong nhan duoc token.";
    return;
  }

  try {
    const user = await fetchMe(accessToken);
    if (user.role !== "admin") {
      message.value = "Tai khoan khong co quyen admin.";
      return;
    }
    auth.token = accessToken;
    auth.user = user;
    localStorage.setItem("abc_access_token", accessToken);
    router.replace("/dashboard");
  } catch (err) {
    message.value = err instanceof Error ? err.message : "Dang nhap Google that bai.";
  }
});
</script>
