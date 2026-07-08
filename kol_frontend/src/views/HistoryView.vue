<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getKolBookings } from '../services/api'
import type { Booking } from '../types'
import { formatDateTime, formatStatus } from '../utils/format'

const bookings = ref<Booking[]>([])
const loading = ref(true)

const historyBookings = computed(() =>
  bookings.value.filter((booking) => ['completed', 'cancelled'].includes(booking.status)),
)

onMounted(async () => {
  try {
    bookings.value = await getKolBookings()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="glass-panel page-panel rounded-[2rem]">
    <p class="text-sm uppercase tracking-[0.3em] text-fuchsia-300/80">History</p>
    <h3 class="mt-2 text-2xl font-semibold text-white">Completed and cancelled work</h3>

    <div v-if="loading" class="mt-6 text-sm text-slate-400">Loading history...</div>

    <div v-else-if="!historyBookings.length" class="mt-6 rounded-3xl border border-dashed border-white/10 p-6 text-sm text-slate-400">
      There are no completed or cancelled bookings yet.
    </div>

    <div v-else class="mt-6 space-y-4">
      <article
        v-for="booking in historyBookings"
        :key="booking.id"
        class="rounded-[1.75rem] border border-white/8 bg-white/4 p-5"
      >
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div class="min-w-0">
            <p class="truncate text-lg font-semibold text-white">
              {{ booking.guest_name || booking.customer_email || 'Guest booking' }}
            </p>
            <p class="mt-1 text-sm text-slate-400">{{ formatDateTime(booking.scheduled_at) }}</p>
          </div>

          <span
            class="rounded-full px-3 py-1 text-xs uppercase tracking-[0.25em]"
            :class="
              booking.status === 'completed'
                ? 'border border-emerald-400/30 bg-emerald-500/10 text-emerald-200'
                : 'border border-rose-400/30 bg-rose-500/10 text-rose-200'
            "
          >
            {{ formatStatus(booking.status) }}
          </span>
        </div>

        <p class="mt-3 text-sm text-slate-300">{{ booking.notes || 'No notes were attached.' }}</p>
      </article>
    </div>
  </div>
</template>
