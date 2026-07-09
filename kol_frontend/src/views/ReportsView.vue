<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from 'chart.js'
import { Bar, Doughnut, Line } from 'vue-chartjs'
import { getKolBookings, getKolDashboard } from '../services/api'
import type { Booking, DashboardStats } from '../types'
import { useToastStore } from '../stores/toast'
import { getErrorMessage } from '../utils/errors'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Tooltip, Legend, Filler, ArcElement)

const bookings = ref<Booking[]>([])
const stats = ref<DashboardStats | null>(null)
const loading = ref(true)
const errorMessage = ref('')
const toast = useToastStore()

// Period Filter
const filterPeriod = ref<'all' | '30days' | '90days'>('all')

const filteredBookings = computed(() => {
  if (filterPeriod.value === 'all') return bookings.value
  const now = new Date()
  let limit = 30
  if (filterPeriod.value === '90days') limit = 90
  
  const cutoff = new Date(now.getTime() - limit * 24 * 60 * 60 * 1000)
  return bookings.value.filter(b => new Date(b.created_at) >= cutoff)
})

// Metrics based on filter period
const totalBookings = computed(() => filteredBookings.value.length)
const pendingCount = computed(() => filteredBookings.value.filter(b => b.status === 'pending').length)
const confirmedCount = computed(() => filteredBookings.value.filter(b => b.status === 'confirmed').length)
const completedCount = computed(() => filteredBookings.value.filter(b => b.status === 'completed').length)
const cancelledCount = computed(() => filteredBookings.value.filter(b => b.status === 'cancelled').length)

const collectedRevenue = computed(() => {
  // Sum paid bookings or completed bookings
  return filteredBookings.value
    .filter(b => b.payment_status === 'paid' || b.status === 'completed')
    .reduce((sum, b) => sum + (b.total_amount || 0), 0)
})

const unpaidRevenue = computed(() => {
  return filteredBookings.value
    .filter(b => b.payment_status !== 'paid' && b.status !== 'cancelled' && b.status !== 'completed')
    .reduce((sum, b) => sum + (b.total_amount || 0), 0)
})

const conversionRateNum = computed(() => {
  const total = totalBookings.value
  if (!total) return 0
  return Math.round((completedCount.value / total) * 100)
})

const conversionRate = computed(() => `${conversionRateNum.value}%`)

// Table data rows
const monthlyReportRows = computed(() => {
  const series = stats.value?.revenue_by_month
  if (!series || !series.labels.length) return []
  return series.labels.map((label, index) => {
    const gross = series.gross[index] || 0
    const collected = series.collected[index] || 0
    const count = series.booking_counts[index] || 0
    const unpaid = Math.max(0, gross - collected)
    return {
      label,
      count,
      gross,
      collected,
      unpaid
    }
  }).reverse()
})

// Chart.js Style configurations
const textStyleConfig = { color: "#94a3b8", font: { family: "Inter", size: 10 } }
const gridStyleConfig = { color: "rgba(255, 255, 255, 0.05)", drawTicks: false }

const statusData = computed(() => ({
  labels: ['Chờ xử lý', 'Đã xác nhận', 'Hoàn thành', 'Đã hủy'],
  datasets: [
    {
      data: [
        pendingCount.value,
        confirmedCount.value,
        completedCount.value,
        cancelledCount.value,
      ],
      backgroundColor: ['#f59e0b', '#38bdf8', '#10b981', '#fb7185'],
      borderWidth: 0,
    },
  ],
}))

const trendData = computed(() => {
  const series = stats.value?.revenue_by_month ?? { labels: [], gross: [], collected: [], booking_counts: [] }
  return {
    labels: series.labels,
    datasets: [
      {
        label: 'Gross (Doanh thu gộp)',
        data: series.gross,
        borderColor: '#c084fc',
        backgroundColor: 'rgba(192,132,252,0.08)',
        fill: true,
        tension: 0.35,
      },
      {
        label: 'Collected (Đã thu)',
        data: series.collected,
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34,197,94,0.08)',
        fill: true,
        tension: 0.35,
      },
    ],
  }
})

const workloadData = computed(() => {
  const series = stats.value?.revenue_by_month ?? { labels: [], gross: [], collected: [], booking_counts: [] }
  return {
    labels: series.labels,
    datasets: [
      {
        label: 'Số booking',
        data: series.booking_counts,
        backgroundColor: 'rgba(56, 189, 248, 0.8)',
        borderRadius: 6,
      },
    ],
  }
})

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '72%',
  plugins: { 
    legend: { 
      position: 'bottom' as const,
      labels: { boxWidth: 10, usePointStyle: true, pointStyle: 'circle' as const, color: '#cbd5e1', font: { family: 'Inter', size: 11 } }
    } 
  },
}

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { 
    legend: { 
      position: 'bottom' as const,
      labels: { color: '#cbd5e1', font: { family: 'Inter', size: 11 }, boxWidth: 12, usePointStyle: true, pointStyle: 'circle' as const }
    } 
  },
  scales: {
    x: { 
      grid: { display: false },
      ticks: textStyleConfig
    },
    y: { 
      beginAtZero: true,
      grid: gridStyleConfig,
      ticks: textStyleConfig
    },
  },
}

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { 
      grid: { display: false },
      ticks: textStyleConfig
    },
    y: { 
      beginAtZero: true, 
      grid: gridStyleConfig,
      ticks: { ...textStyleConfig, precision: 0 } 
    },
  },
}

function formatMoney(amount: number) {
  return `${new Intl.NumberFormat('vi-VN').format(amount)} VND`
}

onMounted(async () => {
  try {
    const [dashboardData, bookingData] = await Promise.all([getKolDashboard(), getKolBookings()])
    stats.value = dashboardData
    bookings.value = bookingData
    errorMessage.value = ''
  } catch (error) {
    errorMessage.value = getErrorMessage(
      error,
      'Không tải được dữ liệu báo cáo. Kiểm tra backend và chạy migration mới nhất.',
    )
    toast.error(errorMessage.value)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Top toolbar / Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white">Trung tâm Báo cáo & Phân tích</h1>
        <p class="text-sm text-slate-400">Theo dõi doanh thu, tiến độ và tỷ lệ hoàn thành công việc của bạn.</p>
      </div>

      <!-- Period selector dropdown style -->
      <div class="flex items-center gap-2 shrink-0">
        <span class="text-xs text-slate-400">Thời gian:</span>
        <select 
          v-model="filterPeriod"
          class="h-10 rounded-xl border border-white/10 bg-slate-900 px-3.5 text-xs font-semibold text-slate-200 outline-none transition focus:border-indigo-500 cursor-pointer"
        >
          <option value="all">Toàn thời gian</option>
          <option value="30days">30 ngày gần đây</option>
          <option value="90days">90 ngày gần đây</option>
        </select>
      </div>
    </div>

    <!-- Error message fallback -->
    <section v-if="errorMessage" class="rounded-2xl border border-rose-500/20 bg-rose-500/10 p-5">
      <p class="text-sm font-semibold text-rose-300">Không tải được dữ liệu báo cáo</p>
      <p class="mt-1 text-xs text-rose-300/80 leading-relaxed">{{ errorMessage }}</p>
    </section>

    <!-- Top Key Highlights Cards -->
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <!-- collected_revenue -->
      <div class="relative overflow-hidden rounded-2xl border border-white/8 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl">
        <div class="absolute -top-10 -right-10 w-28 h-28 rounded-full bg-emerald-500/10 blur-2xl" />
        <div class="absolute inset-y-0 left-0 w-1 bg-emerald-500 rounded-r-full" />
        <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400 pl-1">Thực thu (Đã thu)</p>
        <p class="mt-3.5 text-2xl font-bold text-white pl-1 truncate">{{ formatMoney(collectedRevenue) }}</p>
        <p class="mt-2 text-xs text-slate-400 pl-1">Số tiền đã vào tài khoản</p>
      </div>

      <!-- completion_rate -->
      <div class="relative overflow-hidden rounded-2xl border border-white/8 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl">
        <div class="absolute -top-10 -right-10 w-28 h-28 rounded-full bg-indigo-500/10 blur-2xl" />
        <div class="absolute inset-y-0 left-0 w-1 bg-indigo-500 rounded-r-full" />
        <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400 pl-1">Tỉ lệ hoàn thành</p>
        <div class="mt-3.5 flex items-baseline gap-2 pl-1">
          <span class="text-3xl font-bold text-white">{{ conversionRate }}</span>
        </div>
        <div class="mt-3 w-full bg-white/5 rounded-full h-1.5 overflow-hidden">
          <div class="bg-indigo-500 h-full rounded-full transition-all duration-500" :style="{ width: conversionRate }" />
        </div>
      </div>

      <!-- completed_bookings -->
      <div class="relative overflow-hidden rounded-2xl border border-white/8 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl">
        <div class="absolute -top-10 -right-10 w-28 h-28 rounded-full bg-sky-500/10 blur-2xl" />
        <div class="absolute inset-y-0 left-0 w-1 bg-sky-500 rounded-r-full" />
        <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400 pl-1">Đã hoàn thành</p>
        <p class="mt-3.5 text-3xl font-bold text-white pl-1">{{ completedCount }}</p>
        <p class="mt-2 text-xs text-slate-400 pl-1">Yêu cầu hoàn tất thành công</p>
      </div>

      <!-- pending_bookings -->
      <div class="relative overflow-hidden rounded-2xl border border-white/8 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl">
        <div class="absolute -top-10 -right-10 w-28 h-28 rounded-full bg-amber-500/10 blur-2xl" />
        <div class="absolute inset-y-0 left-0 w-1 bg-amber-500 rounded-r-full" />
        <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400 pl-1">Chờ xử lý</p>
        <p class="mt-3.5 text-3xl font-bold text-white pl-1">{{ pendingCount }}</p>
        <p class="mt-2 text-xs text-slate-400 pl-1">Lịch hoặc hóa đơn cần duyệt gấp</p>
      </div>
    </div>

    <!-- Charts Row -->
    <div v-if="!loading" class="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
      <!-- Revenue Trend Line Chart -->
      <div class="rounded-3xl border border-white/8 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl flex flex-col justify-between">
        <div class="mb-4">
          <h3 class="text-base font-bold text-white">Xu hướng Doanh thu</h3>
          <p class="text-xs text-slate-400">Thống kê theo 12 tháng gần nhất (gộp và thực thu)</p>
        </div>
        <div class="h-[280px]">
          <Line v-if="stats" :key="JSON.stringify(trendData)" :data="trendData" :options="lineOptions" />
        </div>
      </div>

      <!-- Status Doughnut Chart -->
      <div class="rounded-3xl border border-white/8 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl flex flex-col justify-between">
        <div class="mb-4">
          <h3 class="text-base font-bold text-white">Cơ cấu trạng thái Booking</h3>
          <p class="text-xs text-slate-400">Phân bố trạng thái xử lý các lịch hẹn</p>
        </div>
        <div class="h-[200px] flex items-center justify-center">
          <Doughnut v-if="stats" :key="JSON.stringify(statusData)" :data="statusData" :options="doughnutOptions" />
        </div>
        <div class="mt-4 grid grid-cols-2 gap-2 text-center text-xs">
          <div class="rounded-xl bg-white/5 border border-white/5 p-2">
            <span class="text-slate-400 block mb-0.5">Xác nhận</span>
            <strong class="text-white text-sm">{{ confirmedCount }}</strong>
          </div>
          <div class="rounded-xl bg-white/5 border border-white/5 p-2">
            <span class="text-slate-400 block mb-0.5">Đã hủy</span>
            <strong class="text-white text-sm">{{ cancelledCount }}</strong>
          </div>
        </div>
      </div>
    </div>

    <!-- Workload & Financial Balance Grid -->
    <div v-if="!loading" class="grid gap-6 md:grid-cols-2">
      <!-- Booking Counts bar -->
      <div class="rounded-3xl border border-white/8 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl flex flex-col justify-between">
        <div class="mb-4">
          <h3 class="text-base font-bold text-white">Số booking nhận được</h3>
          <p class="text-xs text-slate-400">Khối lượng công việc nhận về theo các tháng</p>
        </div>
        <div class="h-[240px]">
          <Bar v-if="stats" :key="JSON.stringify(workloadData)" :data="workloadData" :options="barOptions" />
        </div>
      </div>

      <!-- Financial balance meters -->
      <div class="rounded-3xl border border-white/8 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl flex flex-col justify-between">
        <div>
          <h3 class="text-base font-bold text-white">Dòng tiền & Công nợ</h3>
          <p class="text-xs text-slate-400">Kiểm soát nguồn doanh thu chờ thanh toán</p>
        </div>

        <div class="mt-4 space-y-4">
          <!-- Collected vs Outstanding Gauge -->
          <div class="rounded-2xl border border-white/5 bg-black/20 p-4">
            <div class="flex items-center justify-between text-xs mb-2">
              <span class="text-slate-400">Thực thu / Doanh thu gộp</span>
              <span class="font-bold text-emerald-300">
                {{ Math.round((collectedRevenue / (collectedRevenue + unpaidRevenue || 1)) * 100) }}%
              </span>
            </div>
            <div class="w-full bg-white/5 rounded-full h-2.5 overflow-hidden">
              <div 
                class="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all duration-500" 
                :style="{ width: `${Math.round((collectedRevenue / (collectedRevenue + unpaidRevenue || 1)) * 100)}%` }" 
              />
            </div>
          </div>

          <div class="space-y-2 text-xs">
            <div class="flex items-center justify-between rounded-xl bg-emerald-500/5 border border-emerald-500/10 px-3.5 py-2.5">
              <span class="text-emerald-300">Đã thanh toán (Thực thu)</span>
              <strong class="text-emerald-200">{{ formatMoney(collectedRevenue) }}</strong>
            </div>
            <div class="flex items-center justify-between rounded-xl bg-amber-500/5 border border-amber-500/10 px-3.5 py-2.5">
              <span class="text-amber-300">Chờ thanh toán (Công nợ)</span>
              <strong class="text-amber-200">{{ formatMoney(unpaidRevenue) }}</strong>
            </div>
            <div class="flex items-center justify-between rounded-xl bg-white/5 border border-white/5 px-3.5 py-2.5">
              <span class="text-slate-400">Dự kiến (Chưa tính hủy)</span>
              <strong class="text-white">{{ formatMoney(collectedRevenue + unpaidRevenue) }}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Earnings Performance Detailed Table -->
    <div v-if="!loading && monthlyReportRows.length" class="rounded-3xl border border-white/8 bg-slate-900/40 backdrop-blur-xl overflow-hidden shadow-xl">
      <div class="px-5 py-4 border-b border-white/5">
        <h3 class="text-base font-bold text-white">Chi tiết hiệu suất Doanh thu</h3>
        <p class="text-xs text-slate-400">Chi tiết doanh số gộp, thực thu và nợ đọng chia theo từng tháng.</p>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full text-left text-xs">
          <thead class="bg-black/25 text-[10px] uppercase tracking-wider text-slate-400 font-bold">
            <tr>
              <th class="px-5 py-3.5">Tháng</th>
              <th class="px-5 py-3.5">Số booking</th>
              <th class="px-5 py-3.5">Doanh thu gộp</th>
              <th class="px-5 py-3.5">Đã thu (Thực thu)</th>
              <th class="px-5 py-3.5">Công nợ còn tồn</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/5">
            <tr 
              v-for="row in monthlyReportRows" 
              :key="row.label"
              class="hover:bg-white/[0.01] transition"
            >
              <td class="px-5 py-3.5 text-white font-medium">{{ row.label }}</td>
              <td class="px-5 py-3.5 text-slate-300">{{ row.count }} booking</td>
              <td class="px-5 py-3.5 text-indigo-300 font-semibold">{{ formatMoney(row.gross) }}</td>
              <td class="px-5 py-3.5 text-emerald-300 font-semibold">{{ formatMoney(row.collected) }}</td>
              <td class="px-5 py-3.5" :class="row.unpaid > 0 ? 'text-amber-300 font-semibold' : 'text-slate-500'">
                {{ row.unpaid > 0 ? formatMoney(row.unpaid) : '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
