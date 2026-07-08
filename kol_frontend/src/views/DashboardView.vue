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
        label="Tổng booking"
        :value="stats?.total_bookings ?? '--'"
        caption="Mọi yêu cầu gắn với tài khoản creator của bạn"
      />
      <StatCard
        label="Chờ duyệt"
        :value="stats?.pending_bookings ?? '--'"
        caption="Yêu cầu chiến dịch vẫn đang chờ xử lý"
      />
      <StatCard
        label="Sắp diễn ra"
        :value="stats?.upcoming_bookings ?? '--'"
        caption="Lịch đã xác nhận hoặc đang chờ trong tương lai"
      />
    </section>

    <section class="grid gap-4 lg:grid-cols-2">
      <RouterLink
        to="/profile"
        class="glass-panel page-panel rounded-[2rem] transition hover:-translate-y-0.5 hover:border-fuchsia-400/30"
      >
        <p class="text-sm uppercase tracking-[0.3em] text-fuchsia-300/80">Quản lý cá nhân</p>
        <h3 class="mt-3 text-2xl font-semibold text-white">Tùy chỉnh hồ sơ công khai</h3>
        <p class="mt-3 text-sm leading-6 text-slate-300">
          Cập nhật tên hiển thị, bio, avatar, màu sắc, liên hệ và các block layout trên trang công khai của bạn.
        </p>
        <div class="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-fuchsia-200">
          Mở trình quản lý hồ sơ <span aria-hidden="true">-></span>
        </div>
      </RouterLink>

      <div class="glass-panel page-panel rounded-[2rem]">
        <p class="text-sm uppercase tracking-[0.3em] text-violet-300/80">Nhắc nhở workspace</p>
        <h3 class="mt-3 text-2xl font-semibold text-white">Đây là trung tâm điều khiển creator</h3>
        <p class="mt-3 text-sm leading-6 text-slate-300">
          Dùng <span class="font-semibold text-white">Tùy chỉnh hồ sơ</span> để quản lý thương hiệu, rồi xử lý đặt lịch, lịch, lịch sử và báo cáo từ thanh bên.
        </p>
      </div>
    </section>

    <section class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <div class="glass-panel page-panel rounded-[2rem]">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm uppercase tracking-[0.3em] text-fuchsia-300/80">Tổng quan</p>
            <h3 class="mt-2 text-2xl font-semibold text-white">Hàng đợi booking mới nhất</h3>
          </div>
        </div>

        <div v-if="loading" class="mt-6 text-sm text-slate-400">Đang tải bảng điều khiển...</div>

        <div v-else-if="!nextBookings.length" class="mt-6 rounded-3xl border border-dashed border-white/10 p-6 text-sm text-slate-400">
          Chưa có booking. Yêu cầu creator mới sẽ hiện ở đây.
        </div>

        <div v-else class="mt-6 space-y-3">
          <div
            v-for="booking in nextBookings"
            :key="booking.id"
            class="rounded-3xl border border-white/8 bg-white/4 p-4"
          >
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div class="min-w-0">
                <p class="truncate font-medium text-white">{{ booking.guest_name || booking.customer_email || 'Khách đặt lịch' }}</p>
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
        <p class="text-sm uppercase tracking-[0.3em] text-violet-300/80">Luồng việc</p>
        <h3 class="mt-2 text-2xl font-semibold text-white">Nhịp workspace</h3>
        <div class="mt-6 space-y-4">
          <div class="rounded-3xl border border-white/8 bg-white/4 p-4">
            <p class="text-sm text-slate-300">Chờ phản hồi</p>
            <p class="mt-2 text-3xl font-semibold text-white">{{ stats?.pending_bookings ?? 0 }}</p>
          </div>
          <div class="rounded-3xl border border-white/8 bg-white/4 p-4">
            <p class="text-sm text-slate-300">Đà lịch đã book</p>
            <p class="mt-2 text-3xl font-semibold text-white">{{ stats?.upcoming_bookings ?? 0 }}</p>
          </div>
          <div class="rounded-3xl border border-white/8 bg-gradient-to-br from-violet-500/18 to-fuchsia-500/16 p-4">
            <p class="text-sm text-slate-200">Ghi chú creator</p>
            <p class="mt-2 text-sm leading-6 text-slate-100">
              Giữ hồ sơ chỉn chu và xác nhận yêu cầu nhanh để duy trì trải nghiệm thương hiệu cao cấp.
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
