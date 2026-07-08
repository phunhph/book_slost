import { createRouter, createWebHistory } from "vue-router";

import GoogleAuthCallbackView from "@/views/GoogleAuthCallbackView.vue";
import HomeView from "@/views/HomeView.vue";
import KolDetailView from "@/views/KolDetailView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/kol/:username",
      name: "kol-detail",
      component: KolDetailView,
      props: true,
    },
    {
      path: "/auth/google/callback",
      name: "google-auth-callback",
      component: GoogleAuthCallbackView,
    },
  ],
  scrollBehavior() {
    return { top: 0 };
  },
});

export default router;
