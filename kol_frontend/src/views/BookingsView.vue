<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import BookingDetailModal from '../components/bookings/BookingDetailModal.vue'
import { getKolBookings, reviewPaymentProof, updateBookingStatus } from '../services/api'
import type { Booking } from '../types'
import { formatDateTime, formatStatus } from '../utils/format'
import { useToastStore } from '../stores/toast'
import { getErrorMessage } from '../utils/errors'

const toast = useToastStore()
const bookings = ref<Booking[]>([])
const loading = ref(true)
const pendingIds = ref<string[]>([])
const statusFilter = ref<'all' | 'pending' | 'confirmed' | 'proof'>('all')
const query = ref('')
const page = ref(1)
const pageSize = ref(5)
const selected = ref<Booking | null>(null)
const detailOpen = ref(false)

function openDetail(booking: Booking) {
  selected.value = booking
  detailOpen.value = true
}

function closeDetail() {
  detailOpen.value = false
  selected.value = null
}

function paymentLabel(status?: string) {
  return (
    {
      unpaid: 'Chưa thanh toán',
      proof_submitted: 'Chờ duyệt bill',
      paid: 'Đã duyệt TT',
    }[status || ''] ?? (status || '—')
  )
}

const activeBookings = computed(() =>
  bookings.value.filter((booking) => !['completed', 'cancelled'].includes(booking.status)),
)

const filteredBookings = computed(() => {
  let result = activeBookings.value
  if (statusFilter.value === 'proof') {
    result = result.filter((booking) => booking.payment_status === 'proof_submitted')
  } else if (statusFilter.value !== 'all') {
    result = result.filter((booking) => booking.status === statusFilter.value)
  }
  const q = query.value.trim().toLowerCase()
  if (!q) return result
  return result.filter((booking) => {
    const haystack = [
      booking.guest_name,
      booking.customer_email,
      booking.guest_phone,
      booking.notes,
      booking.payment_code,
      booking.status,
      booking.payment_status,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return haystack.includes(q)
  })
})

const filterCounts = computed(() => ({
  all: activeBookings.value.length,
  pending: activeBookings.value.filter((b) => b.status === 'pending').length,
  confirmed: activeBookings.value.filter((b) => b.status === 'confirmed').length,
  proof: activeBookings.value.filter((b) => b.payment_status === 'proof_submitted').length,
}))

const totalPages = computed(() => Math.max(1, Math.ceil(filteredBookings.value.length / pageSize.value)))
const pagedBookings = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredBookings.value.slice(start, start + pageSize.value)
})
const rangeStart = computed(() =>
  filteredBookings.value.length === 0 ? 0 : (page.value - 1) * pageSize.value + 1,
)
const rangeEnd = computed(() => Math.min(page.value * pageSize.value, filteredBookings.value.length))

watch([statusFilter, query, pageSize], () => {
  page.value = 1
})

watch(filteredBookings, () => {
  if (page.value > totalPages.value) page.value = totalPages.value
})

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
    if (selected.value?.id === bookingId) {
      selected.value = updated
    }
  } catch (error) {
    toast.error(getErrorMessage(error, 'Không cập nhật được trạng thái.'))
  } finally {
    pendingIds.value = pendingIds.value.filter((id) => id !== bookingId)
  }
}

async function changeSelectedStatus(status: string) {
  if (!selected.value) return
  await changeStatus(selected.value.id, status)
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

onMounted(loadBookings)
</script>

<template>
  <div class="glass-panel page-panel rounded-[2rem]">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm uppercase tracking-[0.3em] text-fuchsia-300/80">Quản lý booking</p>
        <h3 class="mt-2 text-xl font-semibold text-white sm:text-2xl">Hợp tác đang diễn ra</h3>
      </div>
      <input
        v-model="query"
        type="search"
        placeholder="Tìm khách, SĐT, mã QR..."
        class="h-11 w-full rounded-full border border-white/10 bg-white/5 px-4 text-sm text-white outline-none placeholder:text-slate-500 focus:border-fuchsia-400/40 lg:max-w-xs"
      />
    </div>

    <div class="mt-5 flex flex-wrap gap-2">
      <button
        v-for="item in [
          { id: 'all', label: 'Tất cả', count: filterCounts.all },
          { id: 'proof', label: 'Chờ duyệt bill', count: filterCounts.proof },
          { id: 'pending', label: 'Chờ xử lý', count: filterCounts.pending },
          { id: 'confirmed', label: 'Đã xác nhận', count: filterCounts.confirmed },
        ]"
        :key="item.id"
        type="button"
        class="rounded-full border px-3 py-1.5 text-xs font-semibold transition"
        :class="
          statusFilter === item.id
            ? 'border-fuchsia-300 bg-fuchsia-500/20 text-fuchsia-100'
            : 'border-white/10 bg-white/5 text-slate-300'
        "
        @click="statusFilter = item.id as 'all' | 'pending' | 'confirmed' | 'proof'"
      >
        {{ item.label }} ({{ item.count }})
      </button>
    </div>

    <div v-if="loading" class="mt-6 text-sm text-slate-400">Đang tải booking...</div>

    <div v-else-if="!filteredBookings.length" class="mt-6 rounded-3xl border border-dashed border-white/10 p-6 text-sm text-slate-400">
      Không có booking phù hợp bộ lọc.
    </div>

    <template v-else>
      <div class="mt-6 space-y-4">
        <article
          v-for="booking in pagedBookings"
          :key="booking.id"
          class="cursor-pointer rounded-[1.75rem] border border-white/8 bg-white/4 p-5 transition hover:border-fuchsia-300/30 hover:bg-fuchsia-500/5"
          @click="openDetail(booking)"
        >
          <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <p class="truncate text-lg font-semibold text-white">
                  {{ booking.guest_name || booking.customer_email || 'Khách đặt lịch' }}
                </p>
                <span class="text-[11px] text-slate-500">Xem chi tiết →</span>
              </div>
              <p class="mt-1 text-sm text-slate-400">{{ formatDateTime(booking.scheduled_at) }}</p>
              <p class="mt-2 text-sm text-violet-200">
                {{ booking.pricing_type === 'hourly' ? 'Theo giờ' : 'Theo trận' }}
                × {{ booking.quantity || 1 }}
                ·
                {{ new Intl.NumberFormat('vi-VN').format(booking.total_amount || 0) }}
                {{ booking.currency || 'VND' }}
              </p>
              <p v-if="booking.payment_code" class="mt-1 text-xs text-slate-400">
                Mã QR: {{ booking.payment_code }} · {{ paymentLabel(booking.payment_status) }}
              </p>
              <p
                v-if="booking.payment_status === 'proof_submitted'"
                class="mt-2 text-xs font-medium text-fuchsia-200"
              >
                Khách đã gửi bill — mở chi tiết để đối chiếu.
              </p>
              <p class="mt-3 text-sm text-slate-300">
                {{ booking.notes || 'Chưa có ghi chú.' }}
              </p>
            </div>

            <div class="flex w-full flex-col gap-3 sm:w-auto lg:max-w-xs" @click.stop>
              <span class="w-fit rounded-full border border-fuchsia-400/30 bg-fuchsia-500/10 px-3 py-1 text-xs uppercase tracking-[0.25em] text-fuchsia-200">
                {{ formatStatus(booking.status) }}
              </span>

              <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
                <button
                  class="btn-secondary"
                  type="button"
                  :disabled="pendingIds.includes(booking.id) || booking.payment_status !== 'paid'"
                  :title="
                    booking.payment_status !== 'paid'
                      ? 'Duyệt bill khớp trước khi xác nhận'
                      : undefined
                  "
                  @click="changeStatus(booking.id, 'confirmed')"
                >
                  Xác nhận
                </button>
                <button
                  class="btn-secondary"
                  type="button"
                  :disabled="pendingIds.includes(booking.id)"
                  @click="changeStatus(booking.id, 'completed')"
                >
                  Hoàn thành
                </button>
                <button
                  class="btn-secondary"
                  type="button"
                  :disabled="pendingIds.includes(booking.id)"
                  @click="changeStatus(booking.id, 'pending')"
                >
                  Chờ xử lý
                </button>
                <button
                  class="btn-secondary"
                  type="button"
                  :disabled="pendingIds.includes(booking.id)"
                  @click="changeStatus(booking.id, 'cancelled')"
                >
                  Hủy
                </button>
              </div>
            </div>
          </div>
        </article>
      </div>

      <div
        class="mt-5 flex flex-col gap-3 rounded-[1.25rem] border border-white/8 bg-white/4 px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
      >
        <p class="text-sm text-slate-400">
          Hiển thị
          <span class="font-semibold text-white">{{ rangeStart }}–{{ rangeEnd }}</span>
          / {{ filteredBookings.length }}
        </p>
        <div class="flex flex-wrap items-center gap-2">
          <select
            v-model.number="pageSize"
            class="h-9 rounded-lg border border-white/10 bg-slate-950/40 px-2 text-sm text-slate-200 outline-none"
          >
            <option :value="5">5 / trang</option>
            <option :value="10">10 / trang</option>
            <option :value="20">20 / trang</option>
          </select>
          <button
            type="button"
            class="h-9 rounded-lg border border-white/10 px-3 text-sm text-slate-200 disabled:opacity-40"
            :disabled="page <= 1"
            @click="page -= 1"
          >
            Trước
          </button>
          <span class="px-2 text-sm text-slate-300">{{ page }} / {{ totalPages }}</span>
          <button
            type="button"
            class="h-9 rounded-lg border border-white/10 px-3 text-sm text-slate-200 disabled:opacity-40"
            :disabled="page >= totalPages"
            @click="page += 1"
          >
            Sau
          </button>
        </div>
      </div>
    </template>

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
