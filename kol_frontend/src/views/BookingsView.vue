<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import BookingDetailModal from '../components/bookings/BookingDetailModal.vue'
import {
  createKolManualBooking,
  getKolBookingLogs,
  getKolBookings,
  reviewPaymentProof,
  updateBookingProgress,
  updateBookingStatus,
} from '../services/api'
import type { Booking, BookingActivityLog, KolManualBookingPayload } from '../types'
import { formatDateTime, formatStatus } from '../utils/format'
import { useToastStore } from '../stores/toast'
import { getErrorMessage } from '../utils/errors'

const toast = useToastStore()
const bookings = ref<Booking[]>([])
const loading = ref(true)
const errorMessage = ref('')
const pendingIds = ref<string[]>([])
const statusFilter = ref<'all' | 'pending' | 'confirmed' | 'proof'>('all')
const query = ref('')
const page = ref(1)
const pageSize = ref(5)
const selected = ref<Booking | null>(null)
const selectedLogs = ref<BookingActivityLog[]>([])
const logsLoading = ref(false)
const detailOpen = ref(false)
const createOpen = ref(false)
const manualForm = ref<KolManualBookingPayload>({
  scheduled_at: '',
  pricing_type: 'match',
  quantity: 1,
  guest_name: '',
  guest_phone: '',
  guest_zalo: '',
  guest_messenger: '',
  notes: '',
  source: 'manual',
})

function openDetail(booking: Booking) {
  selected.value = booking
  detailOpen.value = true
  void loadBookingLogs(booking.id)
}

function closeDetail() {
  detailOpen.value = false
  selected.value = null
  selectedLogs.value = []
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
    errorMessage.value = ''
  } catch (error) {
    bookings.value = []
    errorMessage.value = getErrorMessage(
      error,
      'Không tải được booking. Kiểm tra backend và chạy migration mới nhất.',
    )
    toast.error(errorMessage.value)
  } finally {
    loading.value = false
  }
}

async function loadBookingLogs(bookingId: string) {
  logsLoading.value = true
  try {
    selectedLogs.value = await getKolBookingLogs(bookingId)
  } catch (error) {
    selectedLogs.value = []
    toast.error(getErrorMessage(error, 'Không tải được log booking.'))
  } finally {
    logsLoading.value = false
  }
}

async function changeStatus(bookingId: string, status: string) {
  pendingIds.value = [...pendingIds.value, bookingId]
  try {
    const updated = await updateBookingStatus(bookingId, status)
    bookings.value = bookings.value.map((item) => (item.id === bookingId ? updated : item))
    if (selected.value?.id === bookingId) {
      selected.value = updated
      void loadBookingLogs(bookingId)
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
    void loadBookingLogs(bookingId)
    toast.success(action === 'approve' ? 'Đã duyệt bill và xác nhận lịch.' : 'Đã từ chối bill.')
  } catch (error) {
    toast.error(getErrorMessage(error, 'Không duyệt được thanh toán.'))
  } finally {
    pendingIds.value = pendingIds.value.filter((id) => id !== bookingId)
  }
}

async function createManualBooking() {
  try {
    const created = await createKolManualBooking(manualForm.value)
    bookings.value = [created, ...bookings.value]
    createOpen.value = false
    manualForm.value = {
      scheduled_at: '',
      pricing_type: 'match',
      quantity: 1,
      guest_name: '',
      guest_phone: '',
      guest_zalo: '',
      guest_messenger: '',
      notes: '',
      source: 'manual',
    }
    toast.success('Đã tạo booking ngoài hệ thống.')
  } catch (error) {
    toast.error(getErrorMessage(error, 'Không tạo được booking thủ công.'))
  }
}

async function saveProgress(payload: {
  progress_percent: number
  progress_note?: string
  extended_until?: string
  extension_note?: string
}) {
  if (!selected.value) return
  const bookingId = selected.value.id
  pendingIds.value = [...pendingIds.value, bookingId]
  try {
    const updated = await updateBookingProgress(bookingId, payload)
    bookings.value = bookings.value.map((item) => (item.id === bookingId ? updated : item))
    selected.value = updated
    void loadBookingLogs(bookingId)
    toast.success('Đã cập nhật tiến độ booking.')
  } catch (error) {
    toast.error(getErrorMessage(error, 'Không cập nhật được tiến độ.'))
  } finally {
    pendingIds.value = pendingIds.value.filter((id) => id !== bookingId)
  }
}

onMounted(loadBookings)
</script>

<template>
  <div class="glass-panel page-panel workspace-shell-card">
    <div class="workspace-toolbar">
      <div>
        <p class="workspace-eyebrow">Booking</p>
        <h3 class="workspace-title">Theo dõi và xử lý các hợp tác đang diễn ra</h3>
      </div>
      <div class="flex w-full flex-wrap gap-3 lg:w-auto lg:items-center">
        <input
          v-model="query"
          type="search"
          placeholder="Tìm khách, SĐT, mã QR..."
          class="workspace-search"
        />
        <button class="btn-primary text-sm" type="button" @click="createOpen = !createOpen">+ Tạo booking tay</button>
      </div>
    </div>

    <div v-if="createOpen" class="workspace-card workspace-card--soft mt-5">
      <div class="grid gap-3 md:grid-cols-2">
        <input v-model="manualForm.guest_name" class="field" type="text" placeholder="Tên khách / nhãn booking" />
        <input v-model="manualForm.scheduled_at" class="field" type="datetime-local" />
        <input v-model="manualForm.guest_phone" class="field" type="text" placeholder="Số điện thoại" />
        <input v-model="manualForm.guest_zalo" class="field" type="text" placeholder="Zalo" />
        <select v-model="manualForm.pricing_type" class="field">
          <option value="match">Theo trận</option>
          <option value="hourly">Theo giờ</option>
        </select>
        <input v-model.number="manualForm.quantity" class="field" type="number" min="1" placeholder="Số lượng" />
        <select v-model="manualForm.source" class="field">
          <option value="manual">Tạo tay</option>
          <option value="external">Ngoài hệ thống / inbox</option>
        </select>
        <input v-model="manualForm.guest_messenger" class="field" type="text" placeholder="Messenger" />
        <textarea v-model="manualForm.notes" class="field md:col-span-2 min-h-24" placeholder="Ghi chú brief, phát sinh, nguồn lead..." />
      </div>
      <div class="mt-4 flex justify-end gap-2">
        <button class="btn-secondary text-sm" type="button" @click="createOpen = false">Đóng</button>
        <button class="btn-primary text-sm" type="button" @click="createManualBooking">Lưu booking</button>
      </div>
    </div>

    <div v-if="errorMessage" class="workspace-card mt-5 border border-rose-400/20 bg-rose-500/10">
      <p class="workspace-card-title text-rose-100">Không tải được dữ liệu booking</p>
      <p class="mt-2 text-sm leading-6 text-rose-100/90">{{ errorMessage }}</p>
    </div>

    <div class="workspace-chip-group mt-5">
      <button
        v-for="item in [
          { id: 'all', label: 'Tất cả', count: filterCounts.all },
          { id: 'proof', label: 'Chờ duyệt bill', count: filterCounts.proof },
          { id: 'pending', label: 'Chờ xử lý', count: filterCounts.pending },
          { id: 'confirmed', label: 'Đã xác nhận', count: filterCounts.confirmed },
        ]"
        :key="item.id"
        type="button"
        class="workspace-chip"
        :class="{ 'workspace-chip--active': statusFilter === item.id }"
        @click="statusFilter = item.id as 'all' | 'pending' | 'confirmed' | 'proof'"
      >
        {{ item.label }} ({{ item.count }})
      </button>
    </div>

    <div v-if="loading" class="mt-6 text-sm text-slate-400">Đang tải booking...</div>

    <div v-else-if="!filteredBookings.length" class="workspace-empty mt-6">
      Không có booking phù hợp bộ lọc.
    </div>

    <template v-else>
      <div class="workspace-list mt-6">
        <article
          v-for="booking in pagedBookings"
          :key="booking.id"
          class="workspace-list-item cursor-pointer"
          @click="openDetail(booking)"
        >
          <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <p class="truncate text-lg font-semibold text-white">
                  {{ booking.guest_name || booking.customer_email || 'Khách đặt lịch' }}
                </p>
                <span class="workspace-meta">Xem chi tiết →</span>
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
              <div class="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-300">
                <span class="workspace-chip w-fit">{{ booking.source === 'external' ? 'Ngoài hệ thống' : 'Trong hệ thống' }}</span>
                <span class="workspace-chip w-fit">Tiến độ {{ booking.progress_percent ?? 0 }}%</span>
                <span v-if="booking.extension_count" class="workspace-chip w-fit">Gia hạn {{ booking.extension_count }} lần</span>
              </div>
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
              <span class="workspace-chip workspace-chip--active w-fit">
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

      <div class="workspace-footer-bar mt-5">
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
      :logs="selectedLogs"
      :logs-loading="logsLoading"
      :show-actions="true"
      :busy="Boolean(selected && pendingIds.includes(selected.id))"
      @close="closeDetail"
      @change-status="changeSelectedStatus"
      @review-payment="reviewSelectedPayment"
      @update-progress="saveProgress"
    />
  </div>
</template>
