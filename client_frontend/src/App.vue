<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AppHeader from "@/components/layout/AppHeader.vue";
import AuthModal from "@/components/auth/AuthModal.vue";
import ToastContainer from "@/components/ui/ToastContainer.vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const authModalMode = ref<"login" | "register">("login");
const authModalOpen = ref(false);
const bootstrapped = ref(false);

const isAuthenticated = computed(() => authStore.isAuthenticated);
const currentUser = computed(() => authStore.userProfile ?? authStore.user);
const authUser = computed(() => authStore.user);
const isKolAccount = computed(() => authStore.user?.role === "kol");
/** While restoring token after F5, keep header in "signed-in" layout to avoid login flash */
const headerAuthenticated = computed(
  () => authStore.isAuthenticated || (!authStore.isReady && authStore.hasStoredSession),
);

function openAuthModal(mode: "login" | "register") {
  if (!authStore.isReady && authStore.hasStoredSession) {
    return;
  }
  authModalMode.value = mode;
  authModalOpen.value = true;
}

function closeAuthModal() {
  authModalOpen.value = false;
}

onMounted(async () => {
  await authStore.initialize();
  bootstrapped.value = true;
});
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-50">
    <AppHeader
      :is-authenticated="headerAuthenticated"
      :current-user="currentUser"
      :auth-user="authUser"
      :is-kol-account="isKolAccount"
      @open-auth="openAuthModal"
      @logout="authStore.logout"
    />

    <main>
      <RouterView v-if="bootstrapped || !authStore.hasStoredSession" @open-auth="openAuthModal" />
      <div v-else class="page-container py-16 text-sm text-slate-400">Đang khôi phục phiên đăng nhập...</div>
    </main>

    <AuthModal
      :is-open="authModalOpen"
      :initial-mode="authModalMode"
      @close="closeAuthModal"
      @authenticated="closeAuthModal"
    />

    <ToastContainer />
  </div>
</template>
