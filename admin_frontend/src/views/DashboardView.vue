<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Tổng quan</h1>
        <p class="text-sm text-slate-500">Tổng quan vận hành hệ thống với biểu đồ từ dữ liệu booking thực tế.</p>
      </div>
      <div class="rounded-lg bg-white px-4 py-3 text-sm text-slate-500 card-shadow">
        Cập nhật lúc <span class="font-semibold text-slate-700">{{ updatedAt }}</span>
      </div>
    </div>

    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard label="Tổng KOL" :value="stats?.total_kols ?? 0" color="primary" />
      <StatCard label="Khách hàng" :value="stats?.total_customers ?? 0" color="success" />
      <StatCard label="Tổng booking" :value="stats?.total_bookings ?? 0" color="info" />
      <StatCard label="Chờ xử lý" :value="stats?.pending_bookings ?? 0" color="warning" />
    </div>

    <div class="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <section class="rounded-xl border border-[var(--sb-card-border)] bg-white p-5 card-shadow">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h2 class="text-lg font-bold text-slate-800">Xu hướng booking</h2>
            <p class="text-sm text-slate-500">Số booking phát sinh trong 6 tháng gần nhất</p>
          </div>
        </div>
        <div class="h-[240px] sm:h-[300px] lg:h-[320px]">
          <Bar :data="bookingTrendData" :options="barOptions" />
        </div>
      </section>

      <section class="rounded-xl border border-[var(--sb-card-border)] bg-white p-5 card-shadow">
        <div class="mb-5">
          <h2 class="text-lg font-bold text-slate-800">Trạng thái booking</h2>
          <p class="text-sm text-slate-500">Tỷ trọng theo từng trạng thái xử lý</p>
        </div>
        <div class="mx-auto h-[240px] max-w-[320px] sm:h-[300px] lg:h-[320px]">
          <Doughnut :data="bookingStatusData" :options="doughnutOptions" />
        </div>
      </section>
    </div>

    <div class="grid gap-6 lg:grid-cols-[1.35fr_1fr]">
      <section class="rounded-xl border border-[var(--sb-card-border)] bg-white p-5 card-shadow">
        <div class="mb-5">
          <h2 class="text-lg font-bold text-slate-800">Quy mô hệ thống</h2>
          <p class="text-sm text-slate-500">So sánh các nhóm dữ liệu chính trong hệ thống</p>
        </div>
        <div class="h-[240px] sm:h-[280px] lg:h-[300px]">
          <Bar :data="systemOverviewData" :options="horizontalBarOptions" />
        </div>
      </section>

      <section class="rounded-xl border border-[var(--sb-card-border)] bg-white p-5 card-shadow">
        <div class="mb-5">
          <h2 class="text-lg font-bold text-slate-800">Nhận định nhanh</h2>
          <p class="text-sm text-slate-500">Insight nhanh cho admin theo tình trạng hiện tại</p>
        </div>
        <div class="space-y-4">
          <div class="rounded-lg border border-slate-100 bg-slate-50 px-4 py-3">
            <div class="text-xs font-bold uppercase tracking-wider text-[var(--sb-primary)]">Booking mở</div>
            <div class="mt-1 text-sm text-slate-600">
              <span class="font-bold text-slate-800">{{ openBookings }}</span> booking đang ở trạng thái chờ xử lý/đã xác nhận.
            </div>
          </div>
          <div class="rounded-lg border border-slate-100 bg-slate-50 px-4 py-3">
            <div class="text-xs font-bold uppercase tracking-wider text-emerald-600">Tỷ lệ chuyển đổi</div>
            <div class="mt-1 text-sm text-slate-600">
              <span class="font-bold text-slate-800">{{ completionRate }}%</span> booking đã hoàn thành trên tổng booking.
            </div>
          </div>
          <div class="rounded-lg border border-slate-100 bg-slate-50 px-4 py-3">
            <div class="text-xs font-bold uppercase tracking-wider text-cyan-600">Tập trung KOL</div>
            <div class="mt-1 text-sm text-slate-600">
              KOL có nhiều booking nhất:
              <span class="font-bold text-slate-800">{{ busiestKol }}</span>
            </div>
          </div>
          <div class="rounded-lg border border-slate-100 bg-slate-50 px-4 py-3">
            <div class="text-xs font-bold uppercase tracking-wider text-violet-600">Độ đầy đủ dữ liệu</div>
            <div class="mt-1 text-sm text-slate-600">
              <span class="font-bold text-slate-800">{{ activeKols }}/{{ kols.length }}</span> KOL đang active,
              <span class="font-bold text-slate-800"> {{ customersWithPhone }}/{{ customers.length }}</span> khách hàng có SĐT.
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
  Legend,
  LinearScale,
  Tooltip
} from "chart.js";
import { computed, onMounted, ref } from "vue";
import { Bar, Doughnut } from "vue-chartjs";

import { fetchBookings, fetchCustomers, fetchDashboard, fetchKols } from "@/api/auth";
import StatCard from "@/components/StatCard.vue";
import { useAuthStore } from "@/stores/auth";
import type { BookingRow, CustomerRow, DashboardStats, KolRow } from "@/types";

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend);

const auth = useAuthStore();
const stats = ref<DashboardStats | null>(null);
const bookings = ref<BookingRow[]>([]);
const kols = ref<KolRow[]>([]);
const customers = ref<CustomerRow[]>([]);

const updatedAt = computed(() => new Date().toLocaleString("vi-VN"));

const statusCounts = computed(() => {
  const counts = { pending: 0, confirmed: 0, completed: 0, cancelled: 0 };
  bookings.value.forEach((booking) => {
    if (booking.status in counts) {
      counts[booking.status as keyof typeof counts] += 1;
    }
  });
  return counts;
});

const bookingTrendData = computed(() => {
  const now = new Date();
  const labels: string[] = [];
  const counts: number[] = [];

  for (let i = 5; i >= 0; i -= 1) {
    const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
    labels.push(date.toLocaleDateString("vi-VN", { month: "short", year: "2-digit" }));
    counts.push(0);
  }

  bookings.value.forEach((booking) => {
    const scheduled = new Date(booking.scheduled_at);
    const diffMonths = (scheduled.getFullYear() - now.getFullYear()) * 12 + (scheduled.getMonth() - now.getMonth());
    const index = diffMonths + 5;
    if (index >= 0 && index < counts.length) {
      counts[index] += 1;
    }
  });

  return {
    labels,
    datasets: [
      {
        label: "Booking",
        data: counts,
        backgroundColor: "rgba(78, 115, 223, 0.85)",
        borderRadius: 8,
        maxBarThickness: 42
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

const systemOverviewData = computed(() => ({
  labels: ["KOL", "Khách hàng", "Booking", "Đang chờ xử lý"],
  datasets: [
    {
      label: "Số lượng",
      data: [
        stats.value?.total_kols ?? 0,
        stats.value?.total_customers ?? 0,
        stats.value?.total_bookings ?? 0,
        stats.value?.pending_bookings ?? 0
      ],
      backgroundColor: ["#4e73df", "#1cc88a", "#36b9cc", "#f6c23e"],
      borderRadius: 8
    }
  ]
}));

const openBookings = computed(() => statusCounts.value.pending + statusCounts.value.confirmed);
const completionRate = computed(() => {
  const total = stats.value?.total_bookings ?? 0;
  if (!total) return 0;
  return Math.round((statusCounts.value.completed / total) * 100);
});
const activeKols = computed(() => kols.value.filter((item) => item.is_active).length);
const customersWithPhone = computed(() => customers.value.filter((item) => Boolean(item.phone)).length);

const busiestKol = computed(() => {
  if (!bookings.value.length) return "Chưa có dữ liệu";
  const countMap = new Map<string, number>();
  bookings.value.forEach((booking) => {
    const name = booking.kol_display_name || booking.kol_username || "Không rõ";
    countMap.set(name, (countMap.get(name) ?? 0) + 1);
  });
  return [...countMap.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] ?? "Chưa có dữ liệu";
});

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    x: { grid: { display: false } },
    y: { beginAtZero: true, ticks: { precision: 0 } }
  }
};

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: "68%",
  plugins: {
    legend: {
      position: "bottom" as const,
      labels: { boxWidth: 12, usePointStyle: true, pointStyle: "circle" }
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
    x: { beginAtZero: true, ticks: { precision: 0 } },
    y: { grid: { display: false } }
  }
};

onMounted(async () => {
  if (!auth.token) return;
  const [dashboardStats, bookingRows, kolRows, customerRows] = await Promise.all([
    fetchDashboard(auth.token),
    fetchBookings(auth.token),
    fetchKols(auth.token),
    fetchCustomers(auth.token)
  ]);
  stats.value = dashboardStats;
  bookings.value = bookingRows;
  kols.value = kolRows;
  customers.value = customerRows;
});
</script>
