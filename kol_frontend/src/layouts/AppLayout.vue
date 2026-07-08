<script setup lang="ts">
import {
  ArrowRightStartOnRectangleIcon,
  Bars3Icon,
  CalendarDaysIcon,
  ChartBarSquareIcon,
  ClipboardDocumentListIcon,
  HomeIcon,
  UserCircleIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'
import { computed, ref } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const mobileMenuOpen = ref(false)

const navItems = [
  { label: 'Dashboard', to: '/dashboard', icon: HomeIcon },
  { label: 'Customize Profile', to: '/profile', icon: UserCircleIcon },
  { label: 'Bookings', to: '/bookings', icon: ClipboardDocumentListIcon },
  { label: 'Calendar', to: '/calendar', icon: CalendarDaysIcon },
  { label: 'History', to: '/history', icon: ClipboardDocumentListIcon },
  { label: 'Reports', to: '/reports', icon: ChartBarSquareIcon },
]

const initials = computed(() => {
  const source = auth.user?.email || auth.user?.id || 'K'
  return source.slice(0, 2).toUpperCase()
})

const pageTitle = computed(() => {
  const current = navItems.find((item) => item.to === route.path)
  return current?.label ?? 'Workspace'
})

async function signOut() {
  mobileMenuOpen.value = false
  auth.logout()
  await router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-transparent text-slate-100">
    <div class="mx-auto max-w-7xl px-3 py-3 sm:px-4 sm:py-4 lg:px-6">
      <div class="lg:flex lg:gap-6">
        <div class="hidden w-72 shrink-0 lg:block" aria-hidden="true" />

        <aside class="kol-sidebar glass-panel hidden flex-col rounded-[2rem] p-6 lg:flex">
          <div>
            <p class="text-xs uppercase tracking-[0.35em] text-fuchsia-300/80">Creator OS</p>
            <h1 class="mt-3 text-2xl font-semibold text-white">KOL Workspace</h1>
            <p class="mt-2 text-sm text-slate-300">
              Manage your personal brand, public profile, bookings, schedule, and creator performance in one place.
            </p>
          </div>

          <nav class="mt-8 space-y-2">
            <RouterLink
              v-for="item in navItems"
              :key="item.to"
              :to="item.to"
              class="flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition"
              :class="
                route.path === item.to
                  ? 'bg-gradient-to-r from-violet-500/30 to-fuchsia-500/30 text-white'
                  : 'text-slate-300 hover:bg-white/5 hover:text-white'
              "
            >
              <component :is="item.icon" class="size-5 shrink-0" />
              <span class="truncate">{{ item.label }}</span>
            </RouterLink>
          </nav>

          <div class="mt-auto rounded-3xl border border-white/8 bg-white/4 p-4">
            <p class="text-xs uppercase tracking-[0.25em] text-slate-400">Signed in as</p>
            <p class="mt-2 truncate font-medium text-white">{{ auth.user?.email }}</p>
            <p class="mt-1 text-sm text-slate-400">Role: {{ auth.user?.role }}</p>
          </div>
        </aside>

        <div class="min-w-0 flex-1">
          <div class="sticky top-0 z-30 space-y-4 bg-[#0f0b1f]/90 pb-2 pt-[env(safe-area-inset-top)] backdrop-blur-xl">
            <header class="glass-panel rounded-[2rem] px-4 py-4 sm:px-5">
              <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div class="min-w-0">
                  <p class="text-xs uppercase tracking-[0.35em] text-violet-300/90">Creator dashboard</p>
                  <h2 class="mt-2 truncate text-xl font-semibold text-white sm:text-2xl">{{ pageTitle }}</h2>
                </div>

                <div class="flex flex-wrap items-center gap-2 sm:gap-3">
                  <div class="flex min-w-0 flex-1 items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-3 py-2 sm:flex-none">
                    <div class="flex size-10 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 text-sm font-semibold text-white">
                      {{ initials }}
                    </div>
                    <div class="min-w-0">
                      <p class="truncate text-sm font-medium text-white">{{ auth.user?.email }}</p>
                      <p class="text-xs text-slate-400">KOL account</p>
                    </div>
                  </div>

                  <button class="btn-secondary flex shrink-0 items-center gap-2" type="button" @click="signOut">
                    <ArrowRightStartOnRectangleIcon class="size-5" />
                    <span class="hidden sm:inline">Logout</span>
                  </button>

                  <button
                    class="btn-secondary flex shrink-0 items-center gap-2 lg:hidden"
                    type="button"
                    :aria-expanded="mobileMenuOpen"
                    aria-controls="kol-mobile-nav"
                    @click="mobileMenuOpen = !mobileMenuOpen"
                  >
                    <XMarkIcon v-if="mobileMenuOpen" class="size-5" />
                    <Bars3Icon v-else class="size-5" />
                    <span class="sr-only">Toggle navigation</span>
                  </button>
                </div>
              </div>
            </header>

            <nav
              id="kol-mobile-nav"
              class="glass-panel mobile-nav-scroll rounded-[2rem] p-3 lg:hidden"
              :class="mobileMenuOpen ? 'block' : 'hidden'"
            >
              <div class="grid gap-2 sm:grid-cols-2">
                <RouterLink
                  v-for="item in navItems"
                  :key="`${item.to}-mobile`"
                  :to="item.to"
                  class="flex items-center gap-2 rounded-2xl px-4 py-3 text-sm transition"
                  :class="
                    route.path === item.to
                      ? 'bg-gradient-to-r from-violet-500/30 to-fuchsia-500/30 text-white'
                      : 'text-slate-300 hover:bg-white/5 hover:text-white'
                  "
                  @click="mobileMenuOpen = false"
                >
                  <component :is="item.icon" class="size-4 shrink-0" />
                  <span>{{ item.label }}</span>
                </RouterLink>
              </div>
            </nav>

            <nav
              class="glass-panel mobile-nav-scroll rounded-[2rem] p-2 lg:hidden"
              :class="mobileMenuOpen ? 'hidden' : 'block'"
            >
              <div class="flex gap-2 overflow-x-auto pb-1">
                <RouterLink
                  v-for="item in navItems"
                  :key="`${item.to}-scroll`"
                  :to="item.to"
                  class="shrink-0 snap-start rounded-2xl px-3 py-2 text-xs transition sm:px-4 sm:text-sm"
                  :class="
                    route.path === item.to
                      ? 'bg-gradient-to-r from-violet-500/30 to-fuchsia-500/30 text-white'
                      : 'text-slate-300 hover:bg-white/5 hover:text-white'
                  "
                >
                  {{ item.label }}
                </RouterLink>
              </div>
            </nav>
          </div>

          <main class="mt-4 min-w-0 pb-[max(0.75rem,env(safe-area-inset-bottom))] sm:mt-6">
            <RouterView />
          </main>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@media (min-width: 1024px) {
  .kol-sidebar {
    position: fixed;
    top: 1rem;
    bottom: 1rem;
    left: max(1.5rem, calc(50% - 40rem + 1.5rem));
    z-index: 40;
    width: 18rem;
    overflow-y: auto;
  }
}
</style>
