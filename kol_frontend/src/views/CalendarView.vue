<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getKolBookings } from '../services/api'
import type { Booking } from '../types'
import { formatDate, formatDateTime, startOfDayKey } from '../utils/format'

const bookings = ref<Booking[]>([])
const loading = ref(true)

const groupedBookings = computed(() => {
  const groups = new Map<string, Booking[]>()

  bookings.value.forEach((booking) => {
    const key = startOfDayKey(booking.scheduled_at)
    const existing = groups.get(key) || []
    existing.push(booking)
    groups.set(key, existing)
  })

  return Array.from(groups.entries()).map(([date, items]) => ({
    date,
    label: formatDate(date),
    items,
  }))
})

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
    <p class="text-sm uppercase tracking-[0.3em] text-violet-300/80">Calendar</p>
    <h3 class="mt-2 text-xl font-semibold text-white sm:text-2xl">Bookings grouped by date</h3>

    <div v-if="loading" class="mt-6 text-sm text-slate-400">Loading calendar...</div>

    <div v-else-if="!groupedBookings.length" class="mt-6 rounded-3xl border border-dashed border-white/10 p-6 text-sm text-slate-400">
      No calendar items available.
    </div>

    <div v-else class="mt-6 grid gap-4 lg:grid-cols-2">
      <section
        v-for="group in groupedBookings"
        :key="group.date"
        class="rounded-[1.75rem] border border-white/8 bg-white/4 p-5"
      >
        <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <h4 class="text-base font-semibold text-white sm:text-lg">{{ group.label }}</h4>
          <span class="w-fit shrink-0 rounded-full bg-violet-500/12 px-3 py-1 text-xs uppercase tracking-[0.25em] text-violet-200">
            {{ group.items.length }} bookings
          </span>
        </div>

        <div class="mt-4 space-y-3">
          <div
            v-for="booking in group.items"
            :key="booking.id"
            class="rounded-3xl border border-white/8 bg-slate-950/35 p-4"
          >
            <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between sm:gap-3">
              <div class="min-w-0">
                <p class="truncate font-medium text-white">
                  {{ booking.guest_name || booking.customer_email || 'Guest booking' }}
                </p>
                <p class="mt-1 text-sm text-slate-400">{{ formatDateTime(booking.scheduled_at) }}</p>
              </div>
              <span class="w-fit shrink-0 text-xs uppercase tracking-[0.25em] text-fuchsia-200">{{ booking.status }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
