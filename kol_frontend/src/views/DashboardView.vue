<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import StatCard from '../components/ui/StatCard.vue'
import { getKolBookings, getKolDashboard } from '../services/api'
import type { Booking, DashboardStats } from '../types'
import { formatDateTime } from '../utils/format'

const stats = ref<DashboardStats | null>(null)
const bookings = ref<Booking[]>([])
const loading = ref(true)

const nextBookings = computed(() => bookings.value.slice(0, 5))

onMounted(async () => {
  try {
    const [dashboardData, bookingData] = await Promise.all([getKolDashboard(), getKolBookings()])
    stats.value = dashboardData
    bookings.value = bookingData
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-6">
    <section class="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
      <StatCard
        label="Total bookings"
        :value="stats?.total_bookings ?? '--'"
        caption="Everything assigned to your creator account"
      />
      <StatCard
        label="Pending approvals"
        :value="stats?.pending_bookings ?? '--'"
        caption="Campaign requests still waiting on action"
      />
      <StatCard
        label="Upcoming sessions"
        :value="stats?.upcoming_bookings ?? '--'"
        caption="Confirmed or pending future schedules"
      />
    </section>

    <section class="grid gap-4 lg:grid-cols-2">
      <RouterLink
        to="/profile"
        class="glass-panel page-panel rounded-[2rem] transition hover:-translate-y-0.5 hover:border-fuchsia-400/30"
      >
        <p class="text-sm uppercase tracking-[0.3em] text-fuchsia-300/80">Personal management</p>
        <h3 class="mt-3 text-2xl font-semibold text-white">Customize your public profile</h3>
        <p class="mt-3 text-sm leading-6 text-slate-300">
          Update display name, bio, avatar, colors, contact info, and layout blocks that appear on your public page.
        </p>
        <div class="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-fuchsia-200">
          Open profile manager <span aria-hidden="true">-></span>
        </div>
      </RouterLink>

      <div class="glass-panel page-panel rounded-[2rem]">
        <p class="text-sm uppercase tracking-[0.3em] text-violet-300/80">Workspace reminder</p>
        <h3 class="mt-3 text-2xl font-semibold text-white">This is your creator control room</h3>
        <p class="mt-3 text-sm leading-6 text-slate-300">
          Use <span class="font-semibold text-white">Customize Profile</span> to manage your personal brand, then handle bookings, calendar, history, and reports from the sidebar.
        </p>
      </div>
    </section>

    <section class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <div class="glass-panel page-panel rounded-[2rem]">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm uppercase tracking-[0.3em] text-fuchsia-300/80">Overview</p>
            <h3 class="mt-2 text-2xl font-semibold text-white">Latest booking queue</h3>
          </div>
        </div>

        <div v-if="loading" class="mt-6 text-sm text-slate-400">Loading dashboard...</div>

        <div v-else-if="!nextBookings.length" class="mt-6 rounded-3xl border border-dashed border-white/10 p-6 text-sm text-slate-400">
          No bookings yet. New creator requests will appear here.
        </div>

        <div v-else class="mt-6 space-y-3">
          <div
            v-for="booking in nextBookings"
            :key="booking.id"
            class="rounded-3xl border border-white/8 bg-white/4 p-4"
          >
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div class="min-w-0">
                <p class="truncate font-medium text-white">{{ booking.guest_name || booking.customer_email || 'Guest booking' }}</p>
                <p class="mt-1 text-sm text-slate-400">{{ formatDateTime(booking.scheduled_at) }}</p>
              </div>
              <span class="w-fit rounded-full border border-fuchsia-400/30 bg-fuchsia-500/10 px-3 py-1 text-xs uppercase tracking-[0.25em] text-fuchsia-200">
                {{ booking.status }}
              </span>
            </div>
            <p v-if="booking.notes" class="mt-3 text-sm text-slate-300">{{ booking.notes }}</p>
          </div>
        </div>
      </div>

      <div class="glass-panel page-panel rounded-[2rem]">
        <p class="text-sm uppercase tracking-[0.3em] text-violet-300/80">Flow</p>
        <h3 class="mt-2 text-2xl font-semibold text-white">Workspace pulse</h3>
        <div class="mt-6 space-y-4">
          <div class="rounded-3xl border border-white/8 bg-white/4 p-4">
            <p class="text-sm text-slate-300">Pending response window</p>
            <p class="mt-2 text-3xl font-semibold text-white">{{ stats?.pending_bookings ?? 0 }}</p>
          </div>
          <div class="rounded-3xl border border-white/8 bg-white/4 p-4">
            <p class="text-sm text-slate-300">Booked calendar momentum</p>
            <p class="mt-2 text-3xl font-semibold text-white">{{ stats?.upcoming_bookings ?? 0 }}</p>
          </div>
          <div class="rounded-3xl border border-white/8 bg-gradient-to-br from-violet-500/18 to-fuchsia-500/16 p-4">
            <p class="text-sm text-slate-200">Creator note</p>
            <p class="mt-2 text-sm leading-6 text-slate-100">
              Keep your profile polished and confirm requests quickly to maintain a premium brand
              experience.
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
