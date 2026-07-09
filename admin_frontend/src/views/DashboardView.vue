<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Tổng quan hệ thống</h1>
        <p class="text-sm text-slate-500">
          Doanh thu toàn hệ thống, xu hướng theo tháng/năm và tình trạng booking.
        </p>
      </div>
      <div class="rounded-lg bg-white px-4 py-3 text-sm text-slate-500 card-shadow">
        Cập nhật lúc <span class="font-semibold text-slate-700">{{ updatedAt }}</span>
      </div>
    </div>

    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Doanh thu đã thu" :value="formatMoney(stats?.collected_revenue)" color="success" />
      <StatCard label="Doanh thu tháng này" :value="formatMoney(stats?.month_collected_revenue)" color="primary" />
      <StatCard label="Doanh thu năm nay" :value="formatMoney(stats?.year_collected_revenue)" color="info" />
      <StatCard label="Chưa thu / chờ TT" :value="formatMoney(stats?.unpaid_revenue)" color="warning" />
    </div>

    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard label="Tổng KOL" :value="stats?.total_kols ?? 0" color="primary" />
      <StatCard label="Khách hàng" :value="stats?.total_customers ?? 0" color="success" />
      <StatCard label="Tổng booking" :value="stats?.total_bookings ?? 0" color="info" />
      <StatCard label="Chờ xử lý" :value="stats?.pending_bookings ?? 0" color="warning" />
    </div>

    <div class="grid gap-6 xl:grid-cols-[2fr_1fr]">
      <section class="rounded-xl border border-[var(--sb-card-border)] bg-white p-5 card-shadow">
        <div class="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-lg font-bold text-slate-800">Doanh thu theo thời gian</h2>
            <p class="text-sm text-slate-500">
              {{ revenuePeriod === 'month' ? '12 tháng gần nhất' : '5 năm gần nhất' }} · gộp toàn hệ thống
            </p>
          </div>
          <div class="inline-flex rounded-lg border border-slate-200 bg-slate-50 p-1">
            <button
              type="button"
              class="rounded-md px-3 py-1.5 text-sm font-semibold transition"
              :class="revenuePeriod === 'month' ? 'bg-white text-[var(--sb-primary)] shadow-sm' : 'text-slate-500'"
              @click="revenuePeriod = 'month'"
            >
              Theo tháng
            </button>
            <button
              type="button"
              class="rounded-md px-3 py-1.5 text-sm font-semibold transition"
              :class="revenuePeriod === 'year' ? 'bg-white text-[var(--sb-primary)] shadow-sm' : 'text-slate-500'"
              @click="revenuePeriod = 'year'"
            >
              Theo năm
            </button>
          </div>
        </div>
        <div class="h-[280px] sm:h-[320px] lg:h-[360px]">
          <Line :data="revenueTrendData" :options="revenueLineOptions" />
        </div>
      </section>

      <section class="rounded-xl border border-[var(--sb-card-border)] bg-white p-5 card-shadow">
        <div class="mb-5">
          <h2 class="text-lg font-bold text-slate-800">Cơ cấu doanh thu</h2>
          <p class="text-sm text-slate-500">Đã thu so với còn phải thu (loại booking hủy)</p>
        </div>
        <div class="mx-auto h-[240px] max-w-[320px] sm:h-[280px]">
          <Doughnut :data="revenueSplitData" :options="doughnutOptions" />
        </div>
        <div class="mt-4 space-y-2 text-sm text-slate-600">
          <div class="flex items-center justify-between rounded-lg bg-emerald-50 px-3 py-2">
            <span>Đã thu</span>
            <strong class="text-emerald-700">{{ formatMoney(stats?.collected_revenue) }}</strong>
          </div>
          <div class="flex items-center justify-between rounded-lg bg-amber-50 px-3 py-2">
            <span>Chưa thu</span>
            <strong class="text-amber-700">{{ formatMoney(stats?.unpaid_revenue) }}</strong>
          </div>
          <div class="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
            <span>Gross (không hủy)</span>
            <strong class="text-slate-800">{{ formatMoney(stats?.gross_revenue) }}</strong>
          </div>
        </div>
      </section>
    </div>

    <div class="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <section class="rounded-xl border border-[var(--sb-card-border)] bg-white p-5 card-shadow">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h2 class="text-lg font-bold text-slate-800">Booking & doanh thu tháng</h2>
            <p class="text-sm text-slate-500">So sánh số booking và doanh thu đã thu theo tháng</p>
          </div>
        </div>
        <div class="h-[260px] sm:h-[300px] lg:h-[320px]">
          <Bar :data="bookingRevenueComboData" :options="comboBarOptions" />
        </div>
      </section>

      <section class="rounded-xl border border-[var(--sb-card-border)] bg-white p-5 card-shadow">
        <div class="mb-5">
          <h2 class="text-lg font-bold text-slate-800">Trạng thái booking</h2>
          <p class="text-sm text-slate-500">Tỷ trọng theo trạng thái xử lý</p>
        </div>
        <div class="mx-auto h-[240px] max-w-[320px] sm:h-[300px]">
          <Doughnut :data="bookingStatusData" :options="doughnutOptions" />
        </div>
      </section>
    </div>

    <div class="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
      <section class="rounded-xl border border-[var(--sb-card-border)] bg-white p-5 card-shadow">
        <div class="mb-5">
          <h2 class="text-lg font-bold text-slate-800">Top KOL theo doanh thu</h2>
          <p class="text-sm text-slate-500">Xếp hạng theo doanh thu đã thu trên toàn hệ thống</p>
        </div>
        <div class="h-[260px] sm:h-[300px]">
          <Bar :data="topKolRevenueData" :options="horizontalBarOptions" />
        </div>
      </section>

      <section class="rounded-xl border border-[var(--sb-card-border)] bg-white p-5 card-shadow">
        <div class="mb-5">
          <h2 class="text-lg font-bold text-slate-800">Nhận định nhanh</h2>
          <p class="text-sm text-slate-500">Tóm tắt vận hành admin</p>
        </div>
        <div class="space-y-4">
          <div class="rounded-lg border border-slate-100 bg-slate-50 px-4 py-3">
            <div class="text-xs font-bold uppercase tracking-wider text-emerald-600">Thu tháng này</div>
            <div class="mt-1 text-sm text-slate-600">
              <span class="font-bold text-slate-800">{{ formatMoney(stats?.month_collected_revenue) }}</span>
              / gross
              <span class="font-bold text-slate-800">{{ formatMoney(stats?.month_gross_revenue) }}</span>
            </div>
          </div>
          <div class="rounded-lg border border-slate-100 bg-slate-50 px-4 py-3">
            <div class="text-xs font-bold uppercase tracking-wider text-cyan-600">Thu năm nay</div>
            <div class="mt-1 text-sm text-slate-600">
              <span class="font-bold text-slate-800">{{ formatMoney(stats?.year_collected_revenue) }}</span>
              / gross
              <span class="font-bold text-slate-800">{{ formatMoney(stats?.year_gross_revenue) }}</span>
            </div>
          </div>
          <div class="rounded-lg border border-slate-100 bg-slate-50 px-4 py-3">
            <div class="text-xs font-bold uppercase tracking-wider text-[var(--sb-primary)]">Booking mở</div>
            <div class="mt-1 text-sm text-slate-600">
              <span class="font-bold text-slate-800">{{ openBookings }}</span> booking chờ xử lý/đã xác nhận.
            </div>
          </div>
          <div class="rounded-lg border border-slate-100 bg-slate-50 px-4 py-3">
            <div class="text-xs font-bold uppercase tracking-wider text-violet-600">Tỷ lệ hoàn thành</div>
            <div class="mt-1 text-sm text-slate-600">
              <span class="font-bold text-slate-800">{{ completionRate }}%</span> booking đã hoàn thành.
            </div>
          </div>
          <div class="rounded-lg border border-slate-100 bg-slate-50 px-4 py-3">
            <div class="text-xs font-bold uppercase tracking-wider text-rose-600">KOL doanh thu cao nhất</div>
            <div class="mt-1 text-sm text-slate-600">
              <span class="font-bold text-slate-800">{{ topKolName }}</span>
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
      borderColor: "#4e73df",
      backgroundColor: "rgba(78, 115, 223, 0.12)",
      fill: true,
      tension: 0.35,
      pointRadius: 3
    },
    {
      label: "Đã thu",
      data: activeRevenueSeries.value.collected,
      borderColor: "#1cc88a",
      backgroundColor: "rgba(28, 200, 138, 0.12)",
      fill: true,
      tension: 0.35,
      pointRadius: 3
    }
  ]
}));

const revenueSplitData = computed(() => ({
  labels: ["Đã thu", "Chưa thu"],
  datasets: [
    {
      data: [stats.value?.collected_revenue ?? 0, stats.value?.unpaid_revenue ?? 0],
      backgroundColor: ["#1cc88a", "#f6c23e"],
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
        backgroundColor: "rgba(54, 185, 204, 0.85)",
        borderRadius: 8,
        yAxisID: "y",
        maxBarThickness: 28
      },
      {
        label: "Doanh thu đã thu",
        data: series.collected,
        backgroundColor: "rgba(28, 200, 138, 0.75)",
        borderRadius: 8,
        yAxisID: "y1",
        maxBarThickness: 28
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
      backgroundColor: ["#f6c23e", "#36b9cc", "#1cc88a", "#858796"],
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
        backgroundColor: "#4e73df",
        borderRadius: 8
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

const revenueLineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: "index" as const, intersect: false },
  plugins: {
    legend: { position: "bottom" as const }
  },
  scales: {
    x: { grid: { display: false } },
    y: {
      beginAtZero: true,
      ticks: { callback: moneyTick }
    }
  }
};

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: "68%",
  plugins: {
    legend: {
      position: "bottom" as const,
      labels: { boxWidth: 12, usePointStyle: true, pointStyle: "circle" as const }
    }
  }
};

const comboBarOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: "index" as const, intersect: false },
  plugins: {
    legend: { position: "bottom" as const }
  },
  scales: {
    x: { grid: { display: false } },
    y: {
      beginAtZero: true,
      position: "left" as const,
      ticks: { precision: 0 },
      title: { display: true, text: "Booking" }
    },
    y1: {
      beginAtZero: true,
      position: "right" as const,
      grid: { drawOnChartArea: false },
      ticks: { callback: moneyTick },
      title: { display: true, text: "VND" }
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
      ticks: { callback: moneyTick }
    },
    y: { grid: { display: false } }
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
