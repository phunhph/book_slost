<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import StatCard from '../components/ui/StatCard.vue'
import { getKolBookings, getKolDashboard } from '../services/api'
import type { Booking, DashboardStats } from '../types'

const bookings = ref<Booking[]>([])
const stats = ref<DashboardStats | null>(null)
const loading = ref(true)

const confirmedCount = computed(() =>
  bookings.value.filter((booking) => booking.status === 'confirmed').length,
)

const completedCount = computed(() =>
  bookings.value.filter((booking) => booking.status === 'completed').length,
)

const conversionRate = computed(() => {
  const total = stats.value?.total_bookings || 0
  if (!total) return '0%'
  return `${Math.round((completedCount.value / total) * 100)}%`
})

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
    <section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard label="Tổng booking" :value="stats?.total_bookings ?? '--'" caption="Tất cả yêu cầu nhận được" />
      <StatCard label="Đã xác nhận" :value="confirmedCount" caption="Sẵn sàng thực hiện" />
      <StatCard label="Đã hoàn thành" :value="completedCount" caption="Hoàn tất thành công" />
      <StatCard label="Tỷ lệ hoàn thành" :value="conversionRate" caption="Hoàn thành so với tổng booking" />
    </section>

    <section class="glass-panel page-panel rounded-[2rem]">
      <p class="text-sm uppercase tracking-[0.3em] text-violet-300/80">Ảnh chụp nhanh</p>
      <h3 class="mt-2 text-xl font-semibold text-white sm:text-2xl">Tóm tắt hiệu suất creator</h3>

      <div v-if="loading" class="mt-6 text-sm text-slate-400">Đang tải dữ liệu báo cáo...</div>

      <div v-else class="mt-6 grid gap-4 md:grid-cols-2">
        <div class="rounded-[1.75rem] border border-white/8 bg-white/4 p-5">
          <p class="text-sm text-slate-300">Tồn đọng chờ xử lý</p>
          <p class="mt-3 text-3xl font-semibold text-white">{{ stats?.pending_bookings ?? 0 }}</p>
          <p class="mt-2 text-sm text-slate-400">Yêu cầu đang chờ phản hồi hoặc xác nhận.</p>
        </div>

        <div class="rounded-[1.75rem] border border-white/8 bg-white/4 p-5">
          <p class="text-sm text-slate-300">Khối lượng sắp tới</p>
          <p class="mt-3 text-3xl font-semibold text-white">{{ stats?.upcoming_bookings ?? 0 }}</p>
          <p class="mt-2 text-sm text-slate-400">Buổi làm việc tương lai vẫn còn trên lịch.</p>
        </div>
      </div>
    </section>
  </div>
</template>
