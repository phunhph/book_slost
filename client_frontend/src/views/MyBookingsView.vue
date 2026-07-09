<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

import { getMyBookings, resolveMediaUrl, uploadPaymentProof } from "@/services/bookings";
import { getErrorMessage } from "@/lib/errors";
import { useAuthStore } from "@/stores/auth";
import { useToastStore } from "@/stores/toast";
import type { BookingResponse } from "@/types/booking";

const auth = useAuthStore();
const toast = useToastStore();
const router = useRouter();

const bookings = ref<BookingResponse[]>([]);
const loading = ref(true);
const filter = ref<"all" | "upcoming" | "history">("all");
const query = ref("");
const page = ref(1);
const pageSize = ref(5);
const uploadingIds = ref<string[]>([]);
const proofNotes = ref<Record<string, string>>({});

const emit = defineEmits<{
  openAuth: [mode: "login" | "register"];
}>();

function statusLabel(status: string) {
  return (
    {
      pending: "Chờ xử lý",
      confirmed: "Đã xác nhận",
      completed: "Hoàn thành",
      cancelled: "Đã hủy",
    }[status] ?? status
  );
}

function paymentLabel(status: string) {
  return (
    {
      unpaid: "Chưa gửi bill / chưa thanh toán",
      proof_submitted: "Đã gửi bill · chờ KOL duyệt",
      paid: "Đã duyệt thanh toán",
    }[status] ?? status
  );
}

function statusClass(status: string) {
  return (
    {
      pending: "border-amber-400/30 bg-amber-500/10 text-amber-100",
      confirmed: "border-sky-400/30 bg-sky-500/10 text-sky-100",
      completed: "border-emerald-400/30 bg-emerald-500/10 text-emerald-100",
      cancelled: "border-slate-400/30 bg-slate-500/10 text-slate-200",
    }[status] ?? "border-white/10 bg-white/5 text-slate-200"
  );
}

function canUploadProof(booking: BookingResponse) {
  return (
    booking.status !== "cancelled" &&
    booking.payment_status !== "paid" &&
    Boolean(auth.accessToken)
  );
}

function formatMoney(amount: number, currency = "VND") {
  return `${new Intl.NumberFormat("vi-VN").format(amount)} ${currency}`;
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("vi-VN");
}

const filteredBookings = computed(() => {
  const now = Date.now();
  let result = bookings.value;
  if (filter.value === "upcoming") {
    result = result.filter(
      (item) =>
        !["completed", "cancelled"].includes(item.status) &&
        new Date(item.scheduled_at).getTime() >= now - 60 * 60 * 1000,
    );
  } else if (filter.value === "history") {
    result = result.filter((item) => ["completed", "cancelled"].includes(item.status));
  }

  const q = query.value.trim().toLowerCase();
  if (!q) return result;
  return result.filter((item) => {
    const haystack = [
      item.kol_display_name,
      item.kol_username,
      item.status,
      item.payment_code,
      item.notes,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return haystack.includes(q);
  });
});

const totalPages = computed(() => Math.max(1, Math.ceil(filteredBookings.value.length / pageSize.value)));
const pagedBookings = computed(() => {
  const start = (page.value - 1) * pageSize.value;
  return filteredBookings.value.slice(start, start + pageSize.value);
});
const rangeStart = computed(() =>
  filteredBookings.value.length === 0 ? 0 : (page.value - 1) * pageSize.value + 1,
);
const rangeEnd = computed(() => Math.min(page.value * pageSize.value, filteredBookings.value.length));

const summary = computed(() => {
  const pending = bookings.value.filter((item) => item.status === "pending").length;
  const confirmed = bookings.value.filter((item) => item.status === "confirmed").length;
  const waitingReview = bookings.value.filter((item) => item.payment_status === "proof_submitted").length;
  const unpaid = bookings.value.filter(
    (item) => item.status !== "cancelled" && item.payment_status === "unpaid",
  ).length;
  return { pending, confirmed, unpaid, waitingReview, total: bookings.value.length };
});

async function onProofSelected(bookingId: string, event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = "";
  if (!file || !auth.accessToken) return;

  uploadingIds.value = [...uploadingIds.value, bookingId];
  try {
    const updated = await uploadPaymentProof(
      bookingId,
      file,
      auth.accessToken,
      proofNotes.value[bookingId],
    );
    bookings.value = bookings.value.map((item) => (item.id === bookingId ? updated : item));
    toast.success("Đã gửi bill. Chờ KOL đối chiếu và duyệt.");
  } catch (error) {
    toast.error(getErrorMessage(error, "Không gửi được bill."));
  } finally {
    uploadingIds.value = uploadingIds.value.filter((id) => id !== bookingId);
  }
}

const filterCounts = computed(() => {
  const now = Date.now();
  const upcoming = bookings.value.filter(
    (item) =>
      !["completed", "cancelled"].includes(item.status) &&
      new Date(item.scheduled_at).getTime() >= now - 60 * 60 * 1000,
  ).length;
  const history = bookings.value.filter((item) =>
    ["completed", "cancelled"].includes(item.status),
  ).length;
  return { all: bookings.value.length, upcoming, history };
});

watch([filter, query, pageSize], () => {
  page.value = 1;
});

watch(filteredBookings, () => {
  if (page.value > totalPages.value) page.value = totalPages.value;
});

async function loadBookings() {
  if (!auth.accessToken) {
    loading.value = false;
    return;
  }
  loading.value = true;
  try {
    bookings.value = await getMyBookings(auth.accessToken);
  } catch (error) {
    toast.error(getErrorMessage(error, "Không tải được booking."));
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await auth.initialize();
  if (!auth.isAuthenticated) {
    // Only prompt login after session restore finished (avoids modal flash on F5)
    emit("openAuth", "login");
    return;
  }
  if (auth.user?.role === "kol") {
    toast.error("Tài khoản KOL vui lòng dùng không gian KOL để quản lý booking.");
    await router.replace("/");
    return;
  }
  await loadBookings();
});
</script>

<template>
  <section class="page-container py-8 sm:py-12">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.28em] text-sky-300">Khách hàng</p>
        <h1 class="mt-3 text-3xl font-semibold text-white sm:text-4xl">Booking của tôi</h1>
        <p class="mt-3 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
          Theo dõi lịch đã đặt, mã QR thanh toán và trạng thái xử lý.
        </p>
      </div>
      <RouterLink
        to="/kol/creator-demo"
        class="rounded-full bg-white px-5 py-3 text-center text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
      >
        Đặt thêm với Creator Demo
      </RouterLink>
    </div>

    <div class="mt-8 flex flex-wrap gap-3">
      <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
        <p class="text-[11px] uppercase tracking-[0.18em] text-slate-400">Tổng</p>
        <p class="mt-1 text-xl font-semibold text-white">{{ summary.total }}</p>
      </div>
      <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
        <p class="text-[11px] uppercase tracking-[0.18em] text-slate-400">Chờ xử lý</p>
        <p class="mt-1 text-xl font-semibold text-amber-200">{{ summary.pending }}</p>
      </div>
      <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
        <p class="text-[11px] uppercase tracking-[0.18em] text-slate-400">Đã xác nhận</p>
        <p class="mt-1 text-xl font-semibold text-sky-200">{{ summary.confirmed }}</p>
      </div>
      <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
        <p class="text-[11px] uppercase tracking-[0.18em] text-slate-400">Chưa TT</p>
        <p class="mt-1 text-xl font-semibold text-rose-200">{{ summary.unpaid }}</p>
      </div>
      <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
        <p class="text-[11px] uppercase tracking-[0.18em] text-slate-400">Chờ duyệt bill</p>
        <p class="mt-1 text-xl font-semibold text-fuchsia-200">{{ summary.waitingReview }}</p>
      </div>
    </div>

    <div class="mt-6 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
      <div class="inline-flex flex-wrap rounded-full border border-white/10 bg-white/5 p-1">
        <button
          v-for="item in [
            { id: 'all', label: 'Tất cả', count: filterCounts.all },
            { id: 'upcoming', label: 'Sắp tới', count: filterCounts.upcoming },
            { id: 'history', label: 'Lịch sử', count: filterCounts.history },
          ]"
          :key="item.id"
          type="button"
          class="rounded-full px-4 py-2 text-sm font-medium transition"
          :class="filter === item.id ? 'bg-white text-slate-900' : 'text-slate-300'"
          @click="filter = item.id as 'all' | 'upcoming' | 'history'"
        >
          {{ item.label }}
          <span class="opacity-70">({{ item.count }})</span>
        </button>
      </div>
      <input
        v-model="query"
        type="search"
        placeholder="Tìm KOL, mã QR, ghi chú..."
        class="h-11 w-full rounded-full border border-white/10 bg-white/5 px-4 text-sm text-white outline-none placeholder:text-slate-500 focus:border-sky-400/40 lg:max-w-sm"
      />
    </div>

    <div v-if="!auth.isAuthenticated" class="mt-8 rounded-[2rem] border border-white/10 bg-white/5 p-6 text-slate-300">
      Vui lòng đăng nhập tài khoản khách để xem booking.
      <button class="ml-3 text-sky-300 underline" type="button" @click="emit('openAuth', 'login')">Đăng nhập</button>
    </div>

    <div v-else-if="loading" class="mt-8 text-sm text-slate-400">Đang tải booking...</div>

    <div
      v-else-if="!filteredBookings.length"
      class="mt-8 rounded-[2rem] border border-dashed border-white/15 bg-white/5 p-8 text-slate-300"
    >
      Chưa có booking trong bộ lọc này.
      <RouterLink class="ml-2 text-sky-300 underline" to="/kol/creator-demo">Đặt lịch với Creator Demo</RouterLink>
    </div>

    <template v-else>
      <div class="mt-8 space-y-4">
        <article
          v-for="booking in pagedBookings"
          :key="booking.id"
          class="rounded-[1.75rem] border border-white/10 bg-white/5 p-5"
        >
          <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <h2 class="text-lg font-semibold text-white">
                  {{ booking.kol_display_name || booking.kol_username || "KOL" }}
                </h2>
                <span
                  class="rounded-full border px-3 py-1 text-xs uppercase tracking-[0.2em]"
                  :class="statusClass(booking.status)"
                >
                  {{ statusLabel(booking.status) }}
                </span>
              </div>
              <p class="mt-2 text-sm text-slate-400">{{ formatDateTime(booking.scheduled_at) }}</p>
              <p class="mt-3 text-sm text-violet-200">
                {{ booking.pricing_type === "hourly" ? "Theo giờ" : "Theo trận" }}
                × {{ booking.quantity }}
                ·
                {{ formatMoney(booking.total_amount, booking.currency) }}
              </p>
              <p class="mt-2 text-sm text-slate-300">{{ booking.notes || "Không có ghi chú." }}</p>
              <p v-if="booking.payment_code" class="mt-2 text-xs text-slate-400">
                Mã QR: {{ booking.payment_code }} · {{ paymentLabel(booking.payment_status) }}
              </p>
              <p v-if="booking.payment_proof_note" class="mt-2 text-xs text-amber-200/90">
                Ghi chú TT: {{ booking.payment_proof_note }}
              </p>
              <RouterLink
                v-if="booking.kol_username"
                :to="`/kol/${booking.kol_username}`"
                class="mt-3 inline-flex text-sm font-medium text-sky-300 hover:text-sky-200"
              >
                Xem hồ sơ KOL
              </RouterLink>

              <div
                v-if="canUploadProof(booking)"
                class="mt-4 rounded-2xl border border-dashed border-white/15 bg-slate-950/30 p-4"
              >
                <p class="text-sm font-medium text-white">Gửi bill chuyển khoản</p>
                <p class="mt-1 text-xs leading-5 text-slate-400">
                  Sau khi chuyển khoản đúng số tiền + nội dung mã QR, tải ảnh biên lai để KOL đối chiếu rồi duyệt lịch.
                </p>
                <input
                  v-model="proofNotes[booking.id]"
                  type="text"
                  maxlength="500"
                  placeholder="Ghi chú (tuỳ chọn)"
                  class="mt-3 h-10 w-full rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none placeholder:text-slate-500"
                />
                <label class="mt-3 inline-flex cursor-pointer items-center justify-center rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-slate-200">
                  {{ uploadingIds.includes(booking.id) ? "Đang gửi..." : "Chọn ảnh bill" }}
                  <input
                    class="hidden"
                    type="file"
                    accept="image/jpeg,image/png,image/webp,image/gif"
                    :disabled="uploadingIds.includes(booking.id)"
                    @change="onProofSelected(booking.id, $event)"
                  />
                </label>
              </div>
            </div>

            <div class="flex shrink-0 flex-col gap-3">
              <div v-if="booking.payment_qr_url && booking.payment_status !== 'paid'">
                <img
                  :src="booking.payment_qr_url"
                  alt="QR thanh toán"
                  class="h-36 w-36 rounded-2xl border border-white/15 bg-white p-2"
                />
              </div>
              <a
                v-if="resolveMediaUrl(booking.payment_proof_url)"
                :href="resolveMediaUrl(booking.payment_proof_url) || '#'"
                target="_blank"
                rel="noopener noreferrer"
                class="block"
              >
                <img
                  :src="resolveMediaUrl(booking.payment_proof_url) || ''"
                  alt="Bill đã gửi"
                  class="h-36 w-36 rounded-2xl border border-emerald-400/30 object-cover"
                />
                <p class="mt-2 text-center text-[11px] text-emerald-200">Bill đã gửi</p>
              </a>
            </div>
          </div>
        </article>
      </div>

      <div
        class="mt-6 flex flex-col gap-3 rounded-[1.5rem] border border-white/10 bg-white/5 px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
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
  </section>
</template>
