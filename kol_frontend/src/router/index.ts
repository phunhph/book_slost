import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/auth/google/callback',
      name: 'google-callback',
      component: () => import('../views/GoogleCallbackView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/',
      component: () => import('../layouts/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue'),
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('../views/ProfileView.vue'),
        },
        {
          path: 'bookings',
          name: 'bookings',
          component: () => import('../views/BookingsView.vue'),
        },
        {
          path: 'calendar',
          name: 'calendar',
          component: () => import('../views/CalendarView.vue'),
        },
        {
          path: 'history',
          name: 'history',
          component: () => import('../views/HistoryView.vue'),
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('../views/ReportsView.vue'),
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  const tokenFromQuery =
    typeof to.query.access_token === 'string' ? to.query.access_token : null

  if (tokenFromQuery) {
    auth.acceptOAuthToken(tokenFromQuery)
    try {
      await auth.finalizeOAuth()
      const nextQuery = { ...to.query }
      delete nextQuery.access_token
      return {
        path: to.path,
        query: nextQuery,
        replace: true,
      }
    } catch {
      auth.logout()
      return '/login'
    }
  }

  if (!auth.initialized) {
    await auth.hydrate()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    }
  }

  if (to.meta.guestOnly && auth.isAuthenticated) {
    return '/dashboard'
  }

  return true
})

export default router
