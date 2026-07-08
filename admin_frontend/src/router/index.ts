import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import AdminLayout from "@/layouts/AdminLayout.vue";
import BookingsView from "@/views/BookingsView.vue";
import CustomersView from "@/views/CustomersView.vue";
import DashboardView from "@/views/DashboardView.vue";
import GoogleCallbackView from "@/views/GoogleCallbackView.vue";
import KolsView from "@/views/KolsView.vue";
import LoginView from "@/views/LoginView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", component: LoginView, meta: { guest: true } },
    { path: "/auth/google/callback", component: GoogleCallbackView, meta: { guest: true } },
    {
      path: "/",
      component: AdminLayout,
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        { path: "", redirect: "/dashboard" },
        { path: "dashboard", component: DashboardView },
        { path: "kols", component: KolsView },
        { path: "customers", component: CustomersView },
        { path: "bookings", component: BookingsView }
      ]
    }
  ]
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (auth.token && !auth.user) {
    try {
      await auth.hydrate();
    } catch {
      auth.logout();
    }
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return "/login";
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return "/login";
  }
  if (to.meta.guest && auth.isAuthenticated && auth.isAdmin) {
    return "/dashboard";
  }
});

export default router;
