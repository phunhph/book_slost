<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import AppHeader from "@/components/layout/AppHeader.vue";
import AuthModal from "@/components/auth/AuthModal.vue";
import ToastContainer from "@/components/ui/ToastContainer.vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const authModalMode = ref<"login" | "register">("login");
const authModalOpen = ref(false);

const isAuthenticated = computed(() => authStore.isAuthenticated);
const currentUser = computed(() => authStore.userProfile ?? authStore.user);
const authUser = computed(() => authStore.user);
const isKolAccount = computed(() => authStore.user?.role === "kol");

function openAuthModal(mode: "login" | "register") {
  authModalMode.value = mode;
  authModalOpen.value = true;
}

function closeAuthModal() {
  authModalOpen.value = false;
}

onMounted(() => {
  void authStore.initialize();
});
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-50">
    <AppHeader
      :is-authenticated="isAuthenticated"
      :current-user="currentUser"
      :auth-user="authUser"
      :is-kol-account="isKolAccount"
      @open-auth="openAuthModal"
      @logout="authStore.logout"
    />

    <main>
      <RouterView @open-auth="openAuthModal" />
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
