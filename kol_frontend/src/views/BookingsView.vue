<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getKolBookings, updateBookingStatus } from '../services/api'
import type { Booking } from '../types'
import { formatDateTime, formatStatus } from '../utils/format'

const bookings = ref<Booking[]>([])
const loading = ref(true)
const pendingIds = ref<string[]>([])

const activeBookings = computed(() =>
  bookings.value.filter((booking) => !['completed', 'cancelled'].includes(booking.status)),
)

async function loadBookings() {
  loading.value = true
  try {
    bookings.value = await getKolBookings()
  } finally {
    loading.value = false
  }
}

async function changeStatus(bookingId: string, status: string) {
  pendingIds.value = [...pendingIds.value, bookingId]
  try {
    const updated = await updateBookingStatus(bookingId, status)
    bookings.value = bookings.value.map((item) => (item.id === bookingId ? updated : item))
  } finally {
    pendingIds.value = pendingIds.value.filter((id) => id !== bookingId)
  }
}

onMounted(loadBookings)
</script>

<template>
  <div class="glass-panel page-panel rounded-[2rem]">
    <p class="text-sm uppercase tracking-[0.3em] text-fuchsia-300/80">Booking manager</p>
    <h3 class="mt-2 text-xl font-semibold text-white sm:text-2xl">Active collaborations</h3>

    <div v-if="loading" class="mt-6 text-sm text-slate-400">Loading bookings...</div>

    <div v-else-if="!activeBookings.length" class="mt-6 rounded-3xl border border-dashed border-white/10 p-6 text-sm text-slate-400">
      No active bookings found.
    </div>

    <div v-else class="mt-6 space-y-4">
      <article
        v-for="booking in activeBookings"
        :key="booking.id"
        class="rounded-[1.75rem] border border-white/8 bg-white/4 p-5"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div class="min-w-0 flex-1">
            <p class="truncate text-lg font-semibold text-white">
              {{ booking.guest_name || booking.customer_email || 'Guest booking' }}
            </p>
            <p class="mt-1 text-sm text-slate-400">{{ formatDateTime(booking.scheduled_at) }}</p>
            <p class="mt-3 text-sm text-slate-300">
              {{ booking.notes || 'No campaign notes shared yet.' }}
            </p>
          </div>

          <div class="flex w-full flex-col gap-3 sm:w-auto lg:max-w-xs">
            <span class="w-fit rounded-full border border-fuchsia-400/30 bg-fuchsia-500/10 px-3 py-1 text-xs uppercase tracking-[0.25em] text-fuchsia-200">
              {{ formatStatus(booking.status) }}
            </span>

            <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
              <button
                class="btn-secondary"
                type="button"
                :disabled="pendingIds.includes(booking.id)"
                @click="changeStatus(booking.id, 'confirmed')"
              >
                Confirm
              </button>
              <button
                class="btn-secondary"
                type="button"
                :disabled="pendingIds.includes(booking.id)"
                @click="changeStatus(booking.id, 'completed')"
              >
                Complete
              </button>
              <button
                class="btn-secondary"
                type="button"
                :disabled="pendingIds.includes(booking.id)"
                @click="changeStatus(booking.id, 'pending')"
              >
                Pending
              </button>
              <button
                class="btn-secondary"
                type="button"
                :disabled="pendingIds.includes(booking.id)"
                @click="changeStatus(booking.id, 'cancelled')"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>
