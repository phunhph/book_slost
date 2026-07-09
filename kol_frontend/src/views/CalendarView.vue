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

// View Mode: 'grid' (Month grid) or 'list' (Plain list)
const viewMode = ref<'grid' | 'list'>('grid')

// Calendar State
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth()) // 0-11
const selectedDateStr = ref(new Date().toISOString().slice(0, 10))

const monthLabel = computed(() => {
  const months = [
    'Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4',
    'Tháng 5', 'Tháng 6', 'Tháng 7', 'Tháng 8',
    'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12'
  ]
  return `${months[currentMonth.value]} năm ${currentYear.value}`
})

const weekdays = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ Nhật']

function prevMonth() {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value -= 1
  } else {
    currentMonth.value -= 1
  }
}

function nextMonth() {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value += 1
  } else {
    currentMonth.value += 1
  }
}

function formatDateString(year: number, month: number, day: number) {
  const d = new Date(Date.UTC(year, month, day))
  return d.toISOString().slice(0, 10)
}

function getBookingsForDate(dateStr: string) {
  return bookings.value.filter(b => startOfDayKey(b.scheduled_at) === dateStr)
}

// Generate calendar cells (days)
const calendarDays = computed(() => {
  const firstDayOfMonth = new Date(currentYear.value, currentMonth.value, 1)
  const lastDayOfMonth = new Date(currentYear.value, currentMonth.value + 1, 0)
  const daysInMonth = lastDayOfMonth.getDate()

  // Day of week (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
  let firstDayOfWeek = firstDayOfMonth.getDay()
  // Adjust to start week on Monday: 0 = Monday, ..., 6 = Sunday
  firstDayOfWeek = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1

  const cells = []

  // Padding days from previous month
  const prevMonthLastDay = new Date(currentYear.value, currentMonth.value, 0).getDate()
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const day = prevMonthLastDay - i
    const dateStr = formatDateString(currentYear.value, currentMonth.value - 1, day)
    cells.push({
      day,
      isCurrentMonth: false,
      dateString: dateStr,
      bookings: getBookingsForDate(dateStr)
    })
  }

  // Days of current month
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = formatDateString(currentYear.value, currentMonth.value, day)
    cells.push({
      day,
      isCurrentMonth: true,
      dateString: dateStr,
      bookings: getBookingsForDate(dateStr)
    })
  }

  // Padding days from next month to make a clean grid
  const totalCells = cells.length
  const nextMonthPadding = totalCells % 7 === 0 ? 0 : 7 - (totalCells % 7)
  for (let day = 1; day <= nextMonthPadding; day++) {
    const dateStr = formatDateString(currentYear.value, currentMonth.value + 1, day)
    cells.push({
      day,
      isCurrentMonth: false,
      dateString: dateStr,
      bookings: getBookingsForDate(dateStr)
    })
  }

  return cells
})

// Selected date bookings list
const activeDayBookings = computed(() => {
  return getBookingsForDate(selectedDateStr.value).sort(
    (a, b) => +new Date(a.scheduled_at) - +new Date(b.scheduled_at)
  )
})

const activeDayLabel = computed(() => {
  return formatDate(selectedDateStr.value)
})

// List view grouped bookings
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

function dotColor(status: string) {
  return (
    {
      pending: 'bg-amber-400',
      confirmed: 'bg-sky-400',
      completed: 'bg-emerald-400',
      cancelled: 'bg-rose-400',
    }[status] ?? 'bg-fuchsia-400'
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
  <div class="glass-panel page-panel workspace-shell-card">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <p class="workspace-eyebrow">Lịch làm việc</p>
        <h3 class="workspace-title">Quản lý và điều phối các yêu cầu booking</h3>
        <p class="workspace-subtitle">
          Chuyển đổi qua lại giữa dạng lưới tháng trực quan hoặc dạng danh sách nhóm theo ngày.
        </p>
      </div>
      
      <!-- View Mode Switcher -->
      <div class="inline-flex rounded-xl bg-black/40 border border-white/10 p-1 shrink-0">
        <button 
          type="button"
          @click="viewMode = 'grid'"
          class="px-4 py-2 rounded-lg text-xs font-semibold transition cursor-pointer"
          :class="viewMode === 'grid' ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white' : 'text-slate-400 hover:text-white'"
        >
          Lưới Lịch
        </button>
        <button 
          type="button"
          @click="viewMode = 'list'"
          class="px-4 py-2 rounded-lg text-xs font-semibold transition cursor-pointer"
          :class="viewMode === 'list' ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white' : 'text-slate-400 hover:text-white'"
        >
          Danh sách
        </button>
      </div>
    </div>

    <div v-if="loading" class="mt-8 text-sm text-slate-400">Đang tải lịch...</div>

    <div v-else class="mt-6">
      
      <!-- 1. MONTHLY CALENDAR GRID VIEW -->
      <template v-if="viewMode === 'grid'">
        <!-- Month Selector Header -->
        <div class="flex items-center justify-between bg-black/20 border border-white/8 rounded-2xl px-5 py-4 mb-4">
          <button 
            type="button" 
            @click="prevMonth"
            class="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-white border border-white/8 transition cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
          </button>
          
          <h4 class="text-sm sm:text-base font-bold text-white tracking-wide uppercase">{{ monthLabel }}</h4>
          
          <button 
            type="button" 
            @click="nextMonth"
            class="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-white border border-white/8 transition cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
            </svg>
          </button>
        </div>

        <!-- Weekdays Header -->
        <div class="grid grid-cols-7 gap-1 text-center mb-1 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          <div v-for="day in weekdays" :key="day" class="py-2 bg-black/10 rounded-lg">
            {{ day }}
          </div>
        </div>

        <!-- Calendar Days Grid -->
        <div class="grid grid-cols-7 gap-1.5">
          <div 
            v-for="(day, index) in calendarDays" 
            :key="`${day.dateString}-${index}`"
            @click="selectedDateStr = day.dateString"
            class="min-h-[4.5rem] sm:min-h-[6rem] rounded-xl border p-2 flex flex-col justify-between transition cursor-pointer text-left select-none"
            :class="[
              day.isCurrentMonth ? 'bg-white/[0.03]' : 'bg-black/25 opacity-30',
              selectedDateStr === day.dateString 
                ? 'border-fuchsia-500/50 bg-fuchsia-500/10 shadow-[0_0_15px_rgba(217,70,239,0.1)]' 
                : 'border-white/5 hover:bg-white/5'
            ]"
          >
            <!-- Day Number & Visual Dots -->
            <div class="flex items-center justify-between">
              <span 
                class="text-xs sm:text-sm font-semibold rounded-lg flex items-center justify-center"
                :class="[
                  selectedDateStr === day.dateString ? 'text-fuchsia-300' : 'text-slate-300',
                  day.dateString === new Date().toISOString().slice(0, 10) ? 'bg-violet-500/20 px-1.5 py-0.5 border border-violet-500/30' : ''
                ]"
              >
                {{ day.day }}
              </span>
              
              <!-- Indicator Dots for Mobile -->
              <div class="flex gap-0.5 sm:hidden">
                <span 
                  v-for="booking in day.bookings.slice(0, 3)" 
                  :key="booking.id"
                  class="size-1.5 rounded-full"
                  :class="dotColor(booking.status)"
                />
                <span v-if="day.bookings.length > 3" class="text-[8px] text-slate-400">+</span>
              </div>
            </div>

            <!-- Booking List snippet inside Cell (Desktop only) -->
            <div class="hidden sm:block mt-1 space-y-1 overflow-hidden">
              <div 
                v-for="booking in day.bookings.slice(0, 2)" 
                :key="booking.id"
                @click.stop="openDetail(booking)"
                class="text-[9px] px-1 py-0.5 rounded truncate font-semibold border flex items-center gap-1 cursor-pointer hover:brightness-125 transition-all"
                :class="statusTone(booking.status)"
              >
                <span class="size-1 rounded-full shrink-0" :class="dotColor(booking.status)" />
                {{ booking.guest_name || 'Khách' }}
              </div>
              <div v-if="day.bookings.length > 2" class="text-[8px] text-slate-400 text-center font-bold">
                +{{ day.bookings.length - 2 }} booking
              </div>
            </div>
          </div>
        </div>

        <!-- Selected Day Bookings Detail Section -->
        <div class="mt-6 border-t border-white/8 pt-5">
          <div class="flex items-center justify-between mb-4">
            <h4 class="text-sm sm:text-base font-bold text-white flex items-center gap-2">
              <span class="inline-block w-2.5 h-2.5 rounded-full bg-fuchsia-500"></span>
              Booking ngày {{ activeDayLabel }}
            </h4>
            <span class="rounded-full bg-white/5 border border-white/10 px-3 py-1 text-xs text-slate-300">
              {{ activeDayBookings.length }} yêu cầu
            </span>
          </div>

          <div v-if="!activeDayBookings.length" class="text-center py-8 bg-black/20 border border-white/5 rounded-2xl text-slate-400 text-sm">
            Không có lịch đặt trong ngày này. Nhấp vào ngày khác trên lưới để xem chi tiết.
          </div>

          <div v-else class="grid gap-3 sm:grid-cols-2">
            <div 
              v-for="booking in activeDayBookings" 
              :key="booking.id"
              @click="openDetail(booking)"
              class="workspace-list-item flex flex-col justify-between cursor-pointer text-left p-4 hover:border-white/20 transition relative"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <p class="text-base font-semibold text-white truncate">
                    {{ booking.guest_name || booking.customer_email || 'Khách đặt lịch' }}
                  </p>
                  <p class="text-xs text-slate-400 mt-1">
                    Thời gian: {{ new Date(booking.scheduled_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) }}
                  </p>
                  <p class="text-xs text-violet-200 mt-1">
                    {{ booking.pricing_type === 'hourly' ? 'Theo giờ' : 'Theo trận' }} × {{ booking.quantity }} · 
                    <strong>{{ new Intl.NumberFormat('vi-VN').format(booking.total_amount || 0) }} {{ booking.currency }}</strong>
                  </p>
                </div>
                <span 
                  class="rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider shrink-0"
                  :class="statusTone(booking.status)"
                >
                  {{ formatStatus(booking.status) }}
                </span>
              </div>
              <div class="mt-3 flex items-center justify-between border-t border-white/5 pt-3">
                <span class="text-xs text-slate-400 truncate max-w-[70%]">
                  QR: {{ booking.payment_code }}
                </span>
                <button 
                  type="button"
                  class="text-xs font-semibold text-fuchsia-300 hover:text-white transition"
                  @click.stop="openDetail(booking)"
                >
                  Chi tiết →
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- 2. PLAIN LIST VIEW (GROUPED BY DAY) -->
      <template v-else>
        <div v-if="!groupedBookings.length" class="workspace-empty py-10 text-center">
          Chưa có booking nào. Yêu cầu mới từ khách sẽ được cập nhật tại đây.
        </div>

        <div v-else class="grid gap-4 lg:grid-cols-2">
          <section
            v-for="group in groupedBookings"
            :key="group.date"
            class="workspace-card"
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
                class="workspace-list-item focus:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-300/50"
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
                      class="rounded-full border border-fuchsia-300/40 bg-fuchsia-500/15 px-3 py-1.5 text-xs font-semibold text-fuchsia-100 transition hover:bg-fuchsia-500/25 cursor-pointer"
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
      </template>

    </div>

    <!-- Booking Detail Modal -->
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
