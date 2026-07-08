<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, watch } from "vue";
import { RouterLink } from "vue-router";

import { createBooking } from "@/services/bookings";
import { useAuthStore } from "@/stores/auth";
import { useToastStore } from "@/stores/toast";
import { getErrorMessage } from "@/lib/errors";
import type { BookingResponse } from "@/types/booking";
import type { UserProfile } from "@/types/profile";

const props = defineProps<{
  kolProfile: UserProfile;
  title?: string;
  subtitle?: string;
}>();

const emit = defineEmits<{
  requestAuth: [];
}>();

type FieldName =
  | "guest_name"
  | "guest_phone"
  | "guest_zalo"
  | "guest_messenger"
  | "pricing_type"
  | "quantity"
  | "scheduled_at"
  | "notes";

const authStore = useAuthStore();
const toast = useToastStore();

const form = reactive({
  guest_name: "",
  guest_phone: "",
  guest_zalo: "",
  guest_messenger: "",
  scheduled_at: "",
  notes: "",
  pricing_type: (props.kolProfile.pricing_type || "match") as "match" | "hourly",
  quantity: 1,
});

const fieldErrors = reactive<Partial<Record<FieldName, string>>>({});
const touched = reactive<Partial<Record<FieldName, boolean>>>({});

const state = reactive({
  isSubmitting: false,
});

const paymentResult = reactive<{
  visible: boolean;
  booking: BookingResponse | null;
}>({
  visible: false,
  booking: null,
});

function closePaymentModal() {
  paymentResult.visible = false;
}

function onPaymentKeydown(event: KeyboardEvent) {
  if (event.key === "Escape" && paymentResult.visible) {
    closePaymentModal();
  }
}

watch(
  () => paymentResult.visible,
  (isOpen) => {
    document.body.style.overflow = isOpen ? "hidden" : "";
  },
);

onMounted(() => window.addEventListener("keydown", onPaymentKeydown));
onUnmounted(() => {
  window.removeEventListener("keydown", onPaymentKeydown);
  document.body.style.overflow = "";
});

const isAuthenticated = computed(() => authStore.isAuthenticated);
const customerProfile = computed(() => authStore.userProfile);

const hasBankAccount = computed(() =>
  Boolean(
    props.kolProfile.bank_code?.trim() &&
      props.kolProfile.bank_account_number?.trim() &&
      props.kolProfile.bank_account_name?.trim(),
  ),
);

const unitPrice = computed(() =>
  form.pricing_type === "match"
    ? props.kolProfile.price_per_match || 0
    : props.kolProfile.price_per_hour || 0,
);

const totalAmount = computed(() => unitPrice.value * (Number(form.quantity) || 0));

const quantityLabel = computed(() =>
  form.pricing_type === "match" ? "Số trận" : "Số giờ",
);

const formattedUnitPrice = computed(() =>
  new Intl.NumberFormat("vi-VN").format(unitPrice.value),
);

const formattedTotal = computed(() =>
  new Intl.NumberFormat("vi-VN").format(totalAmount.value),
);

const minScheduledAt = computed(() => {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
});

watch(
  customerProfile,
  (profile) => {
    if (!profile) {
      return;
    }

    form.guest_name = profile.display_name ?? form.guest_name;
    form.guest_phone = profile.phone ?? form.guest_phone;
    form.guest_zalo = profile.zalo ?? form.guest_zalo;
    form.guest_messenger = profile.messenger ?? form.guest_messenger;
  },
  { immediate: true },
);

function normalizePhone(value: string) {
  return value.replace(/[\s.-]/g, "");
}

function validateField(field: FieldName): string {
  let message = "";
  const name = form.guest_name.trim();
  const phone = normalizePhone(form.guest_phone.trim());
  const quantity = Number(form.quantity);

  if (field === "guest_name") {
    if (!name) message = "Vui lòng nhập họ tên.";
    else if (name.length < 2) message = "Họ tên tối thiểu 2 ký tự.";
  }

  if (field === "guest_phone") {
    if (!phone) message = "Vui lòng nhập số điện thoại.";
    else if (!/^(0|\+84)\d{8,10}$/.test(phone)) {
      message = "Số điện thoại không hợp lệ (ví dụ 0901234567).";
    }
  }

  if (field === "quantity") {
    if (!Number.isFinite(quantity) || quantity < 1) message = "Số lượng tối thiểu là 1.";
    else if (quantity > 100) message = "Số lượng tối đa là 100.";
    else if (!Number.isInteger(quantity)) message = "Số lượng phải là số nguyên.";
  }

  if (field === "scheduled_at") {
    if (!form.scheduled_at) message = "Vui lòng chọn ngày giờ chơi.";
    else if (new Date(form.scheduled_at).getTime() < Date.now() - 60_000) {
      message = "Thời gian chơi phải từ hiện tại trở đi.";
    }
  }

  if (field === "pricing_type") {
    if (unitPrice.value <= 0) {
      message =
        form.pricing_type === "match"
          ? "KOL chưa set giá theo trận."
          : "KOL chưa set giá theo giờ.";
    }
  }

  if (field === "notes" && form.notes.trim().length > 2000) {
    message = "Ghi chú tối đa 2000 ký tự.";
  }

  if (message) fieldErrors[field] = message;
  else delete fieldErrors[field];
  return message;
}

function markTouched(field: FieldName) {
  touched[field] = true;
  validateField(field);
}

function validateForm(): boolean {
  const fields: FieldName[] = [
    "guest_name",
    "guest_phone",
    "pricing_type",
    "quantity",
    "scheduled_at",
    "notes",
  ];
  let ok = true;
  for (const field of fields) {
    touched[field] = true;
    if (validateField(field)) ok = false;
  }
  return ok;
}

function inputClass(field: FieldName) {
  return [
    "w-full rounded-2xl border bg-black/15 px-4 py-3 outline-none transition placeholder:text-slate-400 focus:border-sky-300",
    touched[field] && fieldErrors[field] ? "border-rose-400/70" : "border-white/12",
  ];
}

async function submitBooking() {
  if (!hasBankAccount.value) {
    toast.error("KOL chưa cấu hình tài khoản ngân hàng nên chưa tạo được mã QR thanh toán.");
    return;
  }

  if (!validateForm()) {
    toast.error("Vui lòng sửa các ô đang báo lỗi trước khi gửi.");
    return;
  }

  if (unitPrice.value <= 0) {
    toast.error("KOL chưa thiết lập giá. Vui lòng liên hệ KOL.");
    return;
  }

  state.isSubmitting = true;

  try {
    const response = await createBooking(
      {
        kol_user_id: props.kolProfile.user_id,
        scheduled_at: new Date(form.scheduled_at).toISOString(),
        pricing_type: form.pricing_type,
        quantity: form.quantity,
        notes: form.notes.trim() || undefined,
        guest_name: form.guest_name.trim(),
        guest_phone: form.guest_phone.trim(),
        guest_zalo: form.guest_zalo.trim() || undefined,
        guest_messenger: form.guest_messenger.trim() || undefined,
      },
      authStore.accessToken ?? undefined,
    );

    paymentResult.booking = response;
    paymentResult.visible = true;
    toast.success("Đặt lịch thành công. Quét mã VietQR để thanh toán.");
    form.scheduled_at = "";
    form.notes = "";
  } catch (error) {
    toast.error(getErrorMessage(error, "Đặt lịch thất bại."));
  } finally {
    state.isSubmitting = false;
  }
}
</script>

<template>
  <section class="profile-section" id="booking-section">
    <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <p class="profile-section__label">Đặt lịch</p>
        <h2 class="profile-section__title">{{ title ?? 'Đặt lịch chơi cùng' }}</h2>
        <p v-if="subtitle" class="profile-section__body !mt-2 !opacity-80">{{ subtitle }}</p>
      </div>
      <button
        v-if="!isAuthenticated"
        class="rounded-full border border-white/14 px-4 py-2 text-sm font-medium transition hover:bg-white/8"
        type="button"
        @click="emit('requestAuth')"
      >
        Đăng nhập để tự điền
      </button>
    </div>

    <p class="profile-section__body !mt-4">
      {{ isAuthenticated ? 'Thông tin liên hệ đã được lấy từ hồ sơ của bạn. Bạn vẫn có thể chỉnh trước khi gửi.' : 'Khách có thể đặt lịch trực tiếp. Họ tên và số điện thoại là bắt buộc.' }}
    </p>

    <div
      class="mt-5 rounded-2xl border p-4 text-sm"
      :class="hasBankAccount ? 'border-emerald-400/25 bg-emerald-500/10' : 'border-amber-400/30 bg-amber-500/10'"
    >
      <p class="font-medium" :class="hasBankAccount ? 'text-emerald-100' : 'text-amber-100'">
        {{ hasBankAccount ? 'KOL đã cấu hình tài khoản nhận tiền (VietQR).' : 'KOL chưa cấu hình tài khoản ngân hàng — chưa thể tạo mã QR thanh toán.' }}
      </p>
      <p v-if="hasBankAccount" class="mt-2 opacity-85">
        {{ kolProfile.bank_name || 'Ngân hàng' }} ·
        {{ kolProfile.bank_account_name }} ·
        ****{{ (kolProfile.bank_account_number || '').slice(-4) }}
      </p>
    </div>

    <div class="mt-5 rounded-2xl border border-white/12 bg-black/20 p-4 text-sm">
      <p class="opacity-80">Bảng giá hiện tại</p>
      <div class="mt-3 grid gap-2 sm:grid-cols-2">
        <p>
          Theo trận:
          <strong>{{ new Intl.NumberFormat('vi-VN').format(kolProfile.price_per_match || 0) }} {{ kolProfile.currency || 'VND' }}</strong>
        </p>
        <p>
          Theo giờ:
          <strong>{{ new Intl.NumberFormat('vi-VN').format(kolProfile.price_per_hour || 0) }} {{ kolProfile.currency || 'VND' }}</strong>
        </p>
      </div>
    </div>

    <form class="mt-6 grid gap-4 sm:grid-cols-2" novalidate @submit.prevent="submitBooking">
      <label class="text-sm">
        <span class="mb-2 block opacity-80">Họ tên *</span>
        <input
          v-model="form.guest_name"
          :class="inputClass('guest_name')"
          placeholder="Tên của bạn"
          type="text"
          @blur="markTouched('guest_name')"
          @input="validateField('guest_name')"
        />
        <span v-if="touched.guest_name && fieldErrors.guest_name" class="mt-2 block text-xs text-rose-300">
          {{ fieldErrors.guest_name }}
        </span>
      </label>

      <label class="text-sm">
        <span class="mb-2 block opacity-80">Số điện thoại *</span>
        <input
          v-model="form.guest_phone"
          :class="inputClass('guest_phone')"
          placeholder="0901234567"
          type="tel"
          @blur="markTouched('guest_phone')"
          @input="validateField('guest_phone')"
        />
        <span v-if="touched.guest_phone && fieldErrors.guest_phone" class="mt-2 block text-xs text-rose-300">
          {{ fieldErrors.guest_phone }}
        </span>
      </label>

      <label class="text-sm">
        <span class="mb-2 block opacity-80">Zalo</span>
        <input
          v-model="form.guest_zalo"
          :class="inputClass('guest_zalo')"
          placeholder="Zalo liên hệ"
          type="text"
        />
      </label>

      <label class="text-sm">
        <span class="mb-2 block opacity-80">Messenger</span>
        <input
          v-model="form.guest_messenger"
          :class="inputClass('guest_messenger')"
          placeholder="Messenger"
          type="text"
        />
      </label>

      <label class="text-sm">
        <span class="mb-2 block opacity-80">Kiểu tính giá *</span>
        <select
          v-model="form.pricing_type"
          :class="inputClass('pricing_type')"
          @change="markTouched('pricing_type')"
        >
          <option value="match">Theo trận</option>
          <option value="hourly">Theo giờ</option>
        </select>
        <span v-if="touched.pricing_type && fieldErrors.pricing_type" class="mt-2 block text-xs text-rose-300">
          {{ fieldErrors.pricing_type }}
        </span>
      </label>

      <label class="text-sm">
        <span class="mb-2 block opacity-80">{{ quantityLabel }} *</span>
        <input
          v-model.number="form.quantity"
          :class="inputClass('quantity')"
          min="1"
          max="100"
          type="number"
          @blur="markTouched('quantity')"
          @input="validateField('quantity')"
        />
        <span v-if="touched.quantity && fieldErrors.quantity" class="mt-2 block text-xs text-rose-300">
          {{ fieldErrors.quantity }}
        </span>
      </label>

      <label class="text-sm sm:col-span-2">
        <span class="mb-2 block opacity-80">Thời gian chơi *</span>
        <input
          v-model="form.scheduled_at"
          :class="inputClass('scheduled_at')"
          :min="minScheduledAt"
          type="datetime-local"
          @blur="markTouched('scheduled_at')"
          @change="validateField('scheduled_at')"
        />
        <span v-if="touched.scheduled_at && fieldErrors.scheduled_at" class="mt-2 block text-xs text-rose-300">
          {{ fieldErrors.scheduled_at }}
        </span>
      </label>

      <label class="text-sm sm:col-span-2">
        <span class="mb-2 block opacity-80">Ghi chú</span>
        <textarea
          v-model="form.notes"
          :class="[...inputClass('notes'), 'min-h-32']"
          placeholder="Game muốn chơi, xếp hạng, yêu cầu đặc biệt..."
          @blur="markTouched('notes')"
          @input="validateField('notes')"
        />
        <span v-if="touched.notes && fieldErrors.notes" class="mt-2 block text-xs text-rose-300">
          {{ fieldErrors.notes }}
        </span>
      </label>

      <div class="sm:col-span-2 rounded-2xl border border-white/12 bg-black/20 px-4 py-3 text-sm">
        <p>
          Đơn giá: <strong>{{ formattedUnitPrice }} {{ kolProfile.currency || 'VND' }}</strong>
        </p>
        <p class="mt-1">
          Tổng thanh toán:
          <strong class="text-base">{{ formattedTotal }} {{ kolProfile.currency || 'VND' }}</strong>
        </p>
      </div>

      <button
        class="sm:col-span-2 rounded-2xl px-5 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
        type="submit"
        :disabled="state.isSubmitting || !hasBankAccount"
        :style="{ background: kolProfile.primary_color }"
      >
        {{ state.isSubmitting ? 'Đang gửi yêu cầu...' : 'Gửi đặt lịch & nhận mã QR' }}
      </button>
    </form>

    <Teleport to="body">
      <Transition name="pay-modal">
        <div
          v-if="paymentResult.visible && paymentResult.booking"
          class="fixed inset-0 z-[90] flex items-end justify-center bg-slate-950/75 p-3 backdrop-blur-sm sm:items-center sm:p-6"
          @click.self="closePaymentModal"
        >
          <section
            class="max-h-[92vh] w-full max-w-lg overflow-y-auto rounded-[1.75rem] border border-white/10 bg-[#0f172a] shadow-2xl"
            role="dialog"
            aria-modal="true"
            aria-labelledby="payment-modal-title"
          >
            <header class="sticky top-0 z-10 flex items-start justify-between gap-3 border-b border-white/8 bg-[#0f172a]/95 px-5 py-4 backdrop-blur">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-300">VietQR</p>
                <h3 id="payment-modal-title" class="mt-2 text-xl font-semibold text-white">
                  Thanh toán booking
                </h3>
              </div>
              <button
                type="button"
                class="shrink-0 rounded-full border border-white/10 px-3 py-1.5 text-sm text-slate-300 transition hover:bg-white/5"
                @click="closePaymentModal"
              >
                Đóng
              </button>
            </header>

            <div class="space-y-5 px-5 py-5">
              <div class="grid gap-3 sm:grid-cols-2">
                <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p class="text-[11px] uppercase tracking-[0.18em] text-slate-400">Mã thanh toán</p>
                  <p class="mt-2 font-semibold text-white">{{ paymentResult.booking.payment_code }}</p>
                </div>
                <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p class="text-[11px] uppercase tracking-[0.18em] text-slate-400">Số tiền</p>
                  <p class="mt-2 font-semibold text-emerald-200">
                    {{ new Intl.NumberFormat('vi-VN').format(paymentResult.booking.total_amount) }}
                    {{ paymentResult.booking.currency }}
                  </p>
                </div>
                <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p class="text-[11px] uppercase tracking-[0.18em] text-slate-400">Gói</p>
                  <p class="mt-2 text-sm font-medium text-white">
                    {{ paymentResult.booking.pricing_type === 'match' ? 'Theo trận' : 'Theo giờ' }}
                    × {{ paymentResult.booking.quantity }}
                  </p>
                </div>
                <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p class="text-[11px] uppercase tracking-[0.18em] text-slate-400">Trạng thái</p>
                  <p class="mt-2 text-sm font-medium text-amber-100">
                    {{ paymentResult.booking.payment_status === 'unpaid' ? 'Chưa thanh toán' : paymentResult.booking.payment_status }}
                  </p>
                </div>
              </div>

              <div
                v-if="paymentResult.booking.bank_account_number"
                class="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200"
              >
                <p class="text-[11px] uppercase tracking-[0.18em] text-slate-400">Nhận về</p>
                <p class="mt-2 font-medium text-white">
                  {{ paymentResult.booking.bank_name || 'Ngân hàng' }}
                </p>
                <p class="mt-1">
                  {{ paymentResult.booking.bank_account_name }} ·
                  {{ paymentResult.booking.bank_account_number }}
                </p>
              </div>

              <div
                v-if="paymentResult.booking.payment_qr_url"
                class="flex flex-col items-center gap-4 rounded-2xl border border-white/10 bg-white/5 p-5"
              >
                <img
                  :src="paymentResult.booking.payment_qr_url"
                  alt="Mã VietQR thanh toán"
                  class="h-56 w-56 rounded-2xl border border-white/15 bg-white p-2"
                />
                <p class="text-center text-sm leading-6 text-slate-300">
                  Quét bằng app ngân hàng để chuyển đúng số tiền và nội dung lệnh. Sau đó vào
                  <strong class="text-white">Booking của tôi</strong> để gửi bill chuyển khoản.
                </p>
              </div>

              <div class="flex flex-col gap-2 sm:flex-row">
                <RouterLink
                  to="/my-bookings"
                  class="inline-flex flex-1 items-center justify-center rounded-full bg-white px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
                  @click="closePaymentModal"
                >
                  Gửi bill / xem booking
                </RouterLink>
                <button
                  type="button"
                  class="inline-flex flex-1 items-center justify-center rounded-full border border-white/15 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:bg-white/5"
                  @click="closePaymentModal"
                >
                  Để sau
                </button>
              </div>
            </div>
          </section>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<style scoped>
.pay-modal-enter-active,
.pay-modal-leave-active {
  transition: opacity 0.18s ease;
}
.pay-modal-enter-active section,
.pay-modal-leave-active section {
  transition: transform 0.18s ease, opacity 0.18s ease;
}
.pay-modal-enter-from,
.pay-modal-leave-to {
  opacity: 0;
}
.pay-modal-enter-from section,
.pay-modal-leave-to section {
  opacity: 0;
  transform: translateY(14px) scale(0.98);
}
</style>
