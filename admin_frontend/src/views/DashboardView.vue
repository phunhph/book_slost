<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white">Tổng quan hệ thống</h1>
        <p class="text-sm text-slate-400">
          Doanh thu toàn hệ thống, xu hướng theo tháng/năm và tình trạng booking.
        </p>
      </div>
      <div class="rounded-2xl border border-white/10 bg-slate-900/60 backdrop-blur-xl px-4 py-2.5 text-xs text-slate-400 shadow-lg">
        Cập nhật lúc <span class="font-semibold text-slate-200">{{ updatedAt }}</span>
      </div>
    </div>

    <!-- Revenue metrics -->
    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Doanh thu đã thu" :value="formatMoney(stats?.collected_revenue)" color="success" />
      <StatCard label="Doanh thu tháng này" :value="formatMoney(stats?.month_collected_revenue)" color="primary" />
      <StatCard label="Doanh thu năm nay" :value="formatMoney(stats?.year_collected_revenue)" color="info" />
      <StatCard label="Chưa thu / chờ TT" :value="formatMoney(stats?.unpaid_revenue)" color="warning" />
    </div>

    <!-- Counters -->
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard label="Tổng KOL" :value="stats?.total_kols ?? 0" color="primary" />
      <StatCard label="Khách hàng" :value="stats?.total_customers ?? 0" color="success" />
      <StatCard label="Tổng booking" :value="stats?.total_bookings ?? 0" color="info" />
      <StatCard label="Chờ xử lý" :value="stats?.pending_bookings ?? 0" color="warning" />
    </div>

    <!-- Charts Row 1 -->
    <div class="grid gap-6 xl:grid-cols-[2fr_1fr]">
      <section class="rounded-3xl border border-white/10 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl">
        <div class="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-base font-bold text-white">Doanh thu theo thời gian</h2>
            <p class="text-xs text-slate-400">
              {{ revenuePeriod === 'month' ? '12 tháng gần nhất' : '5 năm gần nhất' }} · gộp toàn hệ thống
            </p>
          </div>
          <div class="inline-flex rounded-xl bg-black/40 border border-white/10 p-1 shrink-0">
            <button
              type="button"
              class="rounded-lg px-3 py-1.5 text-xs font-semibold transition cursor-pointer"
              :class="revenuePeriod === 'month' ? 'bg-gradient-to-r from-indigo-600 to-indigo-500 text-white shadow-md' : 'text-slate-400 hover:text-white'"
              @click="revenuePeriod = 'month'"
            >
              Theo tháng
            </button>
            <button
              type="button"
              class="rounded-lg px-3 py-1.5 text-xs font-semibold transition cursor-pointer"
              :class="revenuePeriod === 'year' ? 'bg-gradient-to-r from-indigo-600 to-indigo-500 text-white shadow-md' : 'text-slate-400 hover:text-white'"
              @click="revenuePeriod = 'year'"
            >
              Theo năm
            </button>
          </div>
        </div>
        <div class="h-[280px] sm:h-[320px] lg:h-[360px]">
          <Line v-if="stats" :key="JSON.stringify(revenueTrendData)" :data="revenueTrendData" :options="revenueLineOptions" />
        </div>
      </section>

      <section class="rounded-3xl border border-white/10 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl">
        <div class="mb-5">
          <h2 class="text-base font-bold text-white">Cơ cấu doanh thu</h2>
          <p class="text-xs text-slate-400">Đã thu so với chưa thu (không bao gồm hủy)</p>
        </div>
        <div class="mx-auto h-[220px] max-w-[280px] sm:h-[250px]">
          <Doughnut v-if="stats" :key="JSON.stringify(revenueSplitData)" :data="revenueSplitData" :options="doughnutOptions" />
        </div>
        <div class="mt-5 space-y-2 text-xs">
          <div class="flex items-center justify-between rounded-xl bg-emerald-500/10 border border-emerald-500/20 px-3.5 py-2.5">
            <span class="text-emerald-300 font-medium">Đã thu</span>
            <strong class="text-emerald-200 text-sm">{{ formatMoney(stats?.collected_revenue) }}</strong>
          </div>
          <div class="flex items-center justify-between rounded-xl bg-amber-500/10 border border-amber-500/20 px-3.5 py-2.5">
            <span class="text-amber-300 font-medium">Chưa thu</span>
            <strong class="text-amber-200 text-sm">{{ formatMoney(stats?.unpaid_revenue) }}</strong>
          </div>
          <div class="flex items-center justify-between rounded-xl bg-white/5 border border-white/5 px-3.5 py-2.5">
            <span class="text-slate-400 font-medium">Gross (không hủy)</span>
            <strong class="text-white text-sm">{{ formatMoney(stats?.gross_revenue) }}</strong>
          </div>
        </div>
      </section>
    </div>

    <!-- Charts Row 2 -->
    <div class="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <section class="rounded-3xl border border-white/10 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl">
        <div class="mb-5">
          <h2 class="text-base font-bold text-white">Booking & doanh thu tháng</h2>
          <p class="text-xs text-slate-400">So sánh số booking và doanh thu đã thu theo tháng</p>
        </div>
        <div class="h-[260px] sm:h-[300px] lg:h-[320px]">
          <Bar v-if="stats" :key="JSON.stringify(bookingRevenueComboData)" :data="bookingRevenueComboData" :options="comboBarOptions" />
        </div>
      </section>

      <section class="rounded-3xl border border-white/10 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl">
        <div class="mb-5">
          <h2 class="text-base font-bold text-white">Trạng thái booking</h2>
          <p class="text-xs text-slate-400">Tỷ trọng theo trạng thái xử lý</p>
        </div>
        <div class="mx-auto h-[240px] max-w-[320px] sm:h-[300px]">
          <Doughnut v-if="stats" :key="JSON.stringify(bookingStatusData)" :data="bookingStatusData" :options="doughnutOptions" />
        </div>
      </section>
    </div>

    <!-- Charts Row 3 -->
    <div class="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
      <section class="rounded-3xl border border-white/10 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl">
        <div class="mb-5">
          <h2 class="text-base font-bold text-white">Top KOL theo doanh thu</h2>
          <p class="text-xs text-slate-400">Xếp hạng theo doanh thu đã thu trên toàn hệ thống</p>
        </div>
        <div class="h-[260px] sm:h-[300px]">
          <Bar v-if="stats" :key="JSON.stringify(topKolRevenueData)" :data="topKolRevenueData" :options="horizontalBarOptions" />
        </div>
      </section>

      <section class="rounded-3xl border border-white/10 bg-slate-900/40 backdrop-blur-xl p-5 shadow-xl">
        <div class="mb-5">
          <h2 class="text-base font-bold text-white">Nhận định nhanh</h2>
          <p class="text-xs text-slate-400">Tóm tắt vận hành admin</p>
        </div>
        <div class="space-y-3.5 text-xs text-slate-300">
          <div class="rounded-2xl border border-white/5 bg-white/5 p-4">
            <div class="text-[10px] font-bold uppercase tracking-wider text-emerald-400">Thu tháng này</div>
            <div class="mt-1.5 text-sm font-medium">
              <span class="font-bold text-white">{{ formatMoney(stats?.month_collected_revenue) }}</span>
              <span class="text-slate-400 font-normal"> / gross </span>
              <span class="font-bold text-white">{{ formatMoney(stats?.month_gross_revenue) }}</span>
            </div>
          </div>
          <div class="rounded-2xl border border-white/5 bg-white/5 p-4">
            <div class="text-[10px] font-bold uppercase tracking-wider text-cyan-400">Thu năm nay</div>
            <div class="mt-1.5 text-sm font-medium">
              <span class="font-bold text-white">{{ formatMoney(stats?.year_collected_revenue) }}</span>
              <span class="text-slate-400 font-normal"> / gross </span>
              <span class="font-bold text-white">{{ formatMoney(stats?.year_gross_revenue) }}</span>
            </div>
          </div>
          <div class="rounded-2xl border border-white/5 bg-white/5 p-4">
            <div class="text-[10px] font-bold uppercase tracking-wider text-indigo-400">Booking mở</div>
            <div class="mt-1.5 text-sm font-medium">
              <span class="font-bold text-white">{{ openBookings }}</span> booking đang mở (chờ xử lý / đã xác nhận).
            </div>
          </div>
          <div class="rounded-2xl border border-white/5 bg-white/5 p-4">
            <div class="text-[10px] font-bold uppercase tracking-wider text-purple-400">Vận hành hiệu quả</div>
            <div class="mt-1.5 text-sm font-medium">
              Tỷ lệ hoàn thành: <span class="font-bold text-white">{{ completionRate }}%</span>. KOL có doanh thu cao nhất: <span class="font-bold text-white">{{ topKolName }}</span>.
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip
} from "chart.js";
import { computed, onMounted, ref } from "vue";
import { Bar, Doughnut, Line } from "vue-chartjs";

import { fetchBookings, fetchDashboard } from "@/api/auth";
import StatCard from "@/components/StatCard.vue";
import { useAuthStore } from "@/stores/auth";
import type { BookingRow, DashboardStats } from "@/types";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Filler,
  Tooltip,
  Legend
);

const auth = useAuthStore();
const stats = ref<DashboardStats | null>(null);
const bookings = ref<BookingRow[]>([]);
const revenuePeriod = ref<"month" | "year">("month");

const updatedAt = computed(() => new Date().toLocaleString("vi-VN"));
const currency = computed(() => stats.value?.currency || "VND");

function formatMoney(value?: number | null) {
  const amount = value ?? 0;
  return `${new Intl.NumberFormat("vi-VN").format(amount)} ${currency.value}`;
}

const statusCounts = computed(() => {
  const counts = { pending: 0, confirmed: 0, completed: 0, cancelled: 0 };
  bookings.value.forEach((booking) => {
    if (booking.status in counts) {
      counts[booking.status as keyof typeof counts] += 1;
    }
  });
  if (stats.value?.pending_bookings != null) counts.pending = stats.value.pending_bookings;
  if (stats.value?.confirmed_bookings != null) counts.confirmed = stats.value.confirmed_bookings;
  if (stats.value?.completed_bookings != null) counts.completed = stats.value.completed_bookings;
  if (stats.value?.cancelled_bookings != null) counts.cancelled = stats.value.cancelled_bookings;
  return counts;
});

const activeRevenueSeries = computed(() => {
  if (revenuePeriod.value === "year") {
    return (
      stats.value?.revenue_by_year ?? {
        labels: [],
        gross: [],
        collected: [],
        booking_counts: []
      }
    );
  }
  return (
    stats.value?.revenue_by_month ?? {
      labels: [],
      gross: [],
      collected: [],
      booking_counts: []
    }
  );
});

const revenueTrendData = computed(() => ({
  labels: activeRevenueSeries.value.labels,
  datasets: [
    {
      label: "Gross (không hủy)",
      data: activeRevenueSeries.value.gross,
      borderColor: "#6366f1", // Indigo
      backgroundColor: "rgba(99, 102, 241, 0.08)",
      fill: true,
      tension: 0.35,
      pointRadius: 4,
      pointHoverRadius: 6
    },
    {
      label: "Đã thu",
      data: activeRevenueSeries.value.collected,
      borderColor: "#10b981", // Emerald
      backgroundColor: "rgba(16, 185, 129, 0.08)",
      fill: true,
      tension: 0.35,
      pointRadius: 4,
      pointHoverRadius: 6
    }
  ]
}));

const revenueSplitData = computed(() => ({
  labels: ["Đã thu", "Chưa thu"],
  datasets: [
    {
      data: [stats.value?.collected_revenue ?? 0, stats.value?.unpaid_revenue ?? 0],
      backgroundColor: ["#10b981", "#f59e0b"], // Emerald, Amber
      borderWidth: 0
    }
  ]
}));

const bookingRevenueComboData = computed(() => {
  const series = stats.value?.revenue_by_month ?? {
    labels: [],
    gross: [],
    collected: [],
    booking_counts: []
  };
  return {
    labels: series.labels,
    datasets: [
      {
        label: "Số booking",
        data: series.booking_counts,
        backgroundColor: "rgba(6, 182, 212, 0.75)", // Cyan
        borderRadius: 6,
        yAxisID: "y",
        maxBarThickness: 24
      },
      {
        label: "Doanh thu đã thu",
        data: series.collected,
        backgroundColor: "rgba(16, 185, 129, 0.75)", // Emerald
        borderRadius: 6,
        yAxisID: "y1",
        maxBarThickness: 24
      }
    ]
  };
});

const bookingStatusData = computed(() => ({
  labels: ["Chờ xử lý", "Đã xác nhận", "Hoàn thành", "Đã hủy"],
  datasets: [
    {
      data: [
        statusCounts.value.pending,
        statusCounts.value.confirmed,
        statusCounts.value.completed,
        statusCounts.value.cancelled
      ],
      backgroundColor: ["#f59e0b", "#06b6d4", "#10b981", "#64748b"], // Amber, Cyan, Emerald, Slate
      borderWidth: 0
    }
  ]
}));

const topKolRevenueData = computed(() => {
  const rows = stats.value?.top_kols_by_revenue ?? [];
  return {
    labels: rows.map((item) => item.display_name),
    datasets: [
      {
        label: "Doanh thu đã thu",
        data: rows.map((item) => item.revenue),
        backgroundColor: "#6366f1", // Indigo
        borderRadius: 6,
        maxBarThickness: 24
      }
    ]
  };
});

const openBookings = computed(() => statusCounts.value.pending + statusCounts.value.confirmed);
const completionRate = computed(() => {
  const total = stats.value?.total_bookings ?? 0;
  if (!total) return 0;
  return Math.round((statusCounts.value.completed / total) * 100);
});
const topKolName = computed(() => stats.value?.top_kols_by_revenue?.[0]?.display_name ?? "Chưa có dữ liệu");

const moneyTick = (value: string | number) => {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return String(value);
  if (amount >= 1_000_000) return `${Math.round(amount / 100_000) / 10}tr`;
  if (amount >= 1_000) return `${Math.round(amount / 1000)}k`;
  return `${amount}`;
};

// Styling chart fonts & lines for dark theme
const textStyleConfig = { color: "#94a3b8", font: { family: "Inter", size: 10 } };
const gridStyleConfig = { color: "rgba(255, 255, 255, 0.05)", drawTicks: false };

const revenueLineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: "index" as const, intersect: false },
  plugins: {
    legend: { 
      position: "bottom" as const,
      labels: { color: "#cbd5e1", font: { family: "Inter", size: 11 }, boxWidth: 12, usePointStyle: true, pointStyle: "circle" as const }
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
      ticks: { ...textStyleConfig, callback: moneyTick }
    }
  }
};

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: "72%",
  plugins: {
    legend: {
      position: "bottom" as const,
      labels: { boxWidth: 10, usePointStyle: true, pointStyle: "circle" as const, color: "#cbd5e1", font: { family: "Inter", size: 11 } }
    }
  }
};

const comboBarOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: "index" as const, intersect: false },
  plugins: {
    legend: { 
      position: "bottom" as const,
      labels: { color: "#cbd5e1", font: { family: "Inter", size: 11 }, boxWidth: 12, usePointStyle: true, pointStyle: "circle" as const }
    }
  },
  scales: {
    x: { 
      grid: { display: false },
      ticks: textStyleConfig
    },
    y: {
      beginAtZero: true,
      position: "left" as const,
      grid: gridStyleConfig,
      ticks: textStyleConfig,
      title: { display: true, text: "Booking", color: "#94a3b8", font: { family: "Inter", size: 10 } }
    },
    y1: {
      beginAtZero: true,
      position: "right" as const,
      grid: { drawOnChartArea: false },
      ticks: { ...textStyleConfig, callback: moneyTick },
      title: { display: true, text: "Doanh thu (VND)", color: "#94a3b8", font: { family: "Inter", size: 10 } }
    }
  }
};

const horizontalBarOptions = {
  indexAxis: "y" as const,
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    x: {
      beginAtZero: true,
      grid: gridStyleConfig,
      ticks: { ...textStyleConfig, callback: moneyTick }
    },
    y: { 
      grid: { display: false },
      ticks: textStyleConfig
    }
  }
};

onMounted(async () => {
  if (!auth.token) return;
  const [dashboardStats, bookingRows] = await Promise.all([
    fetchDashboard(auth.token),
    fetchBookings(auth.token)
  ]);
  stats.value = dashboardStats;
  bookings.value = bookingRows;
});
</script>
