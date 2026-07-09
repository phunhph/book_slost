<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import BookingDetailModal from '../components/bookings/BookingDetailModal.vue'
import { getKolBookings, reviewPaymentProof, updateBookingStatus } from '../services/api'
import type { Booking } from '../types'
import { formatDate, formatDateTime, formatStatus, startOfDayKey } from '../utils/format'
import { useToastStore } from '../stores/toast'
import { getErrorMessage } from '../utils/errors'

const toast = useToastStore()
const bookings = ref<Booking[]>([])
const loading = ref(true)
const selected = ref<Booking | null>(null)
const detailOpen = ref(false)
const pendingIds = ref<string[]>([])

const groupedBookings = computed(() => {
  const groups = new Map<string, Booking[]>()

  bookings.value.forEach((booking) => {
    const key = startOfDayKey(booking.scheduled_at)
    const existing = groups.get(key) || []
    existing.push(booking)
    groups.set(key, existing)
  })

  return Array.from(groups.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, items]) => ({
      date,
      label: formatDate(date),
      items: items.slice().sort((a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at)),
    }))
})

function statusTone(status: string) {
  return (
    {
      pending: 'border-amber-400/30 bg-amber-500/10 text-amber-100',
      confirmed: 'border-sky-400/30 bg-sky-500/10 text-sky-100',
      completed: 'border-emerald-400/30 bg-emerald-500/10 text-emerald-100',
      cancelled: 'border-rose-400/30 bg-rose-500/10 text-rose-100',
    }[status] ?? 'border-fuchsia-400/30 bg-fuchsia-500/10 text-fuchsia-100'
  )
}

function openDetail(booking: Booking) {
  selected.value = booking
  detailOpen.value = true
}

function closeDetail() {
  detailOpen.value = false
  selected.value = null
}

async function changeSelectedStatus(status: string) {
  if (!selected.value) return
  const bookingId = selected.value.id
  pendingIds.value = [...pendingIds.value, bookingId]
  try {
    const updated = await updateBookingStatus(bookingId, status)
    bookings.value = bookings.value.map((item) => (item.id === bookingId ? updated : item))
    selected.value = updated
  } catch (error) {
    toast.error(getErrorMessage(error, 'Không cập nhật được trạng thái.'))
  } finally {
    pendingIds.value = pendingIds.value.filter((id) => id !== bookingId)
  }
}

async function reviewSelectedPayment(action: 'approve' | 'reject', note?: string) {
  if (!selected.value) return
  const bookingId = selected.value.id
  pendingIds.value = [...pendingIds.value, bookingId]
  try {
    const updated = await reviewPaymentProof(bookingId, action, note)
    bookings.value = bookings.value.map((item) => (item.id === bookingId ? updated : item))
    selected.value = updated
    toast.success(action === 'approve' ? 'Đã duyệt bill và xác nhận lịch.' : 'Đã từ chối bill.')
  } catch (error) {
    toast.error(getErrorMessage(error, 'Không duyệt được thanh toán.'))
  } finally {
    pendingIds.value = pendingIds.value.filter((id) => id !== bookingId)
  }
}

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
    <p class="text-sm uppercase tracking-[0.3em] text-violet-300/80">Lịch</p>
    <h3 class="mt-2 text-xl font-semibold text-white sm:text-2xl">Booking theo ngày</h3>
    <p class="mt-2 text-sm text-slate-400">
      Bấm vào thẻ booking hoặc nút <span class="text-fuchsia-200">Xem chi tiết</span> để mở đầy đủ thông tin.
    </p>

    <div v-if="loading" class="mt-6 text-sm text-slate-400">Đang tải lịch...</div>

    <div v-else-if="!groupedBookings.length" class="mt-6 rounded-3xl border border-dashed border-white/10 p-6 text-sm text-slate-400">
      Chưa có mục trên lịch.
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
            {{ group.items.length }} booking
          </span>
        </div>

        <div class="mt-4 space-y-3">
          <div
            v-for="booking in group.items"
            :key="booking.id"
            role="button"
            tabindex="0"
            class="rounded-3xl border border-white/8 bg-slate-950/35 p-4 transition hover:border-fuchsia-300/40 hover:bg-fuchsia-500/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-300/50"
            @click="openDetail(booking)"
            @keydown.enter.prevent="openDetail(booking)"
            @keydown.space.prevent="openDetail(booking)"
          >
            <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div class="min-w-0 flex-1">
                <p class="truncate text-base font-semibold text-white">
                  {{ booking.guest_name || booking.customer_email || 'Khách đặt lịch' }}
                </p>
                <p class="mt-1 text-sm text-slate-400">{{ formatDateTime(booking.scheduled_at) }}</p>
                <p class="mt-2 text-sm text-violet-200">
                  {{ booking.pricing_type === 'hourly' ? 'Theo giờ' : 'Theo trận' }}
                  × {{ booking.quantity || 1 }}
                  ·
                  {{ new Intl.NumberFormat('vi-VN').format(booking.total_amount || 0) }}
                  {{ booking.currency || 'VND' }}
                </p>
                <p v-if="booking.guest_phone" class="mt-1 text-xs text-slate-400">SĐT: {{ booking.guest_phone }}</p>
              </div>

              <div class="flex shrink-0 flex-col items-start gap-2 sm:items-end">
                <span
                  class="rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.2em]"
                  :class="statusTone(booking.status)"
                >
                  {{ formatStatus(booking.status) }}
                </span>
                <button
                  type="button"
                  class="rounded-full border border-fuchsia-300/40 bg-fuchsia-500/15 px-3 py-1.5 text-xs font-semibold text-fuchsia-100 transition hover:bg-fuchsia-500/25"
                  @click.stop="openDetail(booking)"
                >
                  Xem chi tiết
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <BookingDetailModal
      :open="detailOpen"
      :booking="selected"
      :show-actions="true"
      :busy="Boolean(selected && pendingIds.includes(selected.id))"
      @close="closeDetail"
      @change-status="changeSelectedStatus"
      @review-payment="reviewSelectedPayment"
    />
  </div>
</template>
