<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import BookingDetailModal from '../components/bookings/BookingDetailModal.vue'
import StatCard from '../components/ui/StatCard.vue'
import { getKolBookings, getKolDashboard } from '../services/api'
import type { Booking, DashboardStats } from '../types'
import { formatDateTime, formatStatus } from '../utils/format'

const stats = ref<DashboardStats | null>(null)
const bookings = ref<Booking[]>([])
const loading = ref(true)
const selected = ref<Booking | null>(null)
const detailOpen = ref(false)

const nextBookings = computed(() => bookings.value.slice(0, 5))

function openDetail(booking: Booking) {
  selected.value = booking
  detailOpen.value = true
}

function closeDetail() {
  detailOpen.value = false
  selected.value = null
}

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
  <div class="workspace-page">
    <!-- HERO DASHBOARD BANNER -->
    <section class="glass-panel page-panel workspace-shell-card workspace-shell-card--hero">
      <div class="workspace-hero">
        <div>
          <p class="workspace-eyebrow">Studio</p>
          <h2 class="workspace-title">Không gian làm việc Creator</h2>
          <p class="workspace-subtitle">
            Theo dõi nhanh các yêu cầu đặt lịch, sắp xếp thời gian biểu và tùy chỉnh trang hồ sơ cá nhân.
          </p>
        </div>
        <div class="workspace-actions">
          <RouterLink to="/profile" class="btn-primary text-sm">Chỉnh hồ sơ</RouterLink>
          <RouterLink to="/bookings" class="btn-secondary text-sm">Mở booking</RouterLink>
        </div>
      </div>
      <div class="workspace-stat-strip mt-6">
        <div class="workspace-stat-pill">
          <p class="workspace-stat-pill__label">Việc nóng</p>
          <p class="workspace-stat-pill__value">{{ stats?.pending_bookings ?? 0 }}</p>
          <p class="workspace-stat-pill__hint">Đang chờ xác nhận</p>
        </div>
        <div class="workspace-stat-pill">
          <p class="workspace-stat-pill__label">Lịch sắp tới</p>
          <p class="workspace-stat-pill__value">{{ stats?.upcoming_bookings ?? 0 }}</p>
          <p class="workspace-stat-pill__hint">Đã chốt lịch hẹn</p>
        </div>
        <div class="workspace-stat-pill">
          <p class="workspace-stat-pill__label">Hồ sơ cá nhân</p>
          <p class="workspace-stat-pill__value">Sẵn sàng</p>
          <p class="workspace-stat-pill__hint">Trang cá nhân công khai</p>
        </div>
      </div>
    </section>

    <!-- KEY METRICS GRID -->
    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard
        label="Tổng booking nhận"
        :value="stats?.total_bookings ?? '--'"
        caption="Tất cả các yêu cầu từ trước tới nay"
      />
      <StatCard
        label="Chờ duyệt"
        :value="stats?.pending_bookings ?? '--'"
        caption="Các booking mới cần phản hồi gấp"
      />
      <StatCard
        label="Lịch sắp tới"
        :value="stats?.upcoming_bookings ?? '--'"
        caption="Lịch chơi game, livestream sắp diễn ra"
      />
      <StatCard
        label="Trạng thái Profile"
        value="Hoạt động"
        caption="Trang đặt lịch đang mở công khai"
      />
    </section>

    <!-- RECENT BOOKINGS & SHORTCUTS -->
    <section class="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
      <!-- Recents List -->
      <div class="glass-panel page-panel workspace-shell-card">
        <div class="workspace-toolbar">
          <div>
            <p class="workspace-eyebrow">Hàng đợi</p>
            <h3 class="workspace-title">Booking mới nhất</h3>
          </div>
          <RouterLink to="/bookings" class="btn-secondary text-sm">Xem tất cả</RouterLink>
        </div>

        <div v-if="loading" class="mt-6 text-sm text-slate-400">Đang tải bảng điều khiển...</div>

        <div v-else-if="!nextBookings.length" class="workspace-empty mt-6">
          Chưa có yêu cầu đặt lịch nào gửi tới bạn.
        </div>

        <div v-else class="workspace-list mt-6">
          <button
            v-for="booking in nextBookings"
            :key="booking.id"
            type="button"
            class="workspace-list-item w-full text-left cursor-pointer transition hover:border-white/25"
            @click="openDetail(booking)"
          >
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="truncate text-base font-semibold text-white">
                    {{ booking.guest_name || booking.customer_email || 'Khách đặt lịch' }}
                  </p>
                  <span class="text-xs text-slate-400 font-normal">Xem chi tiết →</span>
                </div>
                <p class="workspace-card-text mt-1">{{ formatDateTime(booking.scheduled_at) }}</p>
              </div>
              <span class="workspace-chip workspace-chip--active w-fit">
                {{ formatStatus(booking.status) }}
              </span>
            </div>
            <p v-if="booking.notes" class="workspace-card-text mt-3 truncate max-w-2xl opacity-75 italic">"{{ booking.notes }}"</p>
          </button>
        </div>
      </div>

      <!-- Quick Setup Checklist -->
      <div class="glass-panel page-panel workspace-shell-card">
        <p class="workspace-eyebrow">Checklist</p>
        <h3 class="workspace-title">Cấu hình hồ sơ nhanh</h3>
        
        <div class="mt-6 space-y-3">
          <div class="flex items-center gap-3 p-3.5 rounded-2xl bg-white/5 border border-white/8">
            <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold">✓</span>
            <div>
              <p class="text-xs font-semibold text-white">Thiết lập giá</p>
              <p class="text-[10px] text-slate-400 mt-0.5">Đặt biểu phí trận/giờ đầy đủ để mở tính năng đặt lịch.</p>
            </div>
          </div>

          <div class="flex items-center gap-3 p-3.5 rounded-2xl bg-white/5 border border-white/8">
            <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold">✓</span>
            <div>
              <p class="text-xs font-semibold text-white">Tài khoản ngân hàng</p>
              <p class="text-[10px] text-slate-400 mt-0.5">Cấu hình VietQR nhận tiền chuyển khoản tự động.</p>
            </div>
          </div>

          <div class="flex items-center gap-3 p-3.5 rounded-2xl bg-white/5 border border-white/8">
            <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold">✓</span>
            <div>
              <p class="text-xs font-semibold text-white">Thư viện & Liên kết</p>
              <p class="text-[10px] text-slate-400 mt-0.5">Tải ảnh chất lượng cao và gắn link mạng xã hội cá nhân.</p>
            </div>
          </div>
          
          <RouterLink to="/profile" class="mt-4 flex w-full justify-center items-center py-2.5 rounded-xl border border-violet-500/20 bg-violet-500/10 hover:bg-violet-500/20 text-xs font-bold text-violet-300 transition">
            Đi tới Trình Quản Lý Hồ Sơ →
          </RouterLink>
        </div>
      </div>
    </section>

    <BookingDetailModal :open="detailOpen" :booking="selected" @close="closeDetail" />
  </div>
</template>
