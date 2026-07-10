<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { resolveMediaUrl } from '../../services/api'
import type { Booking, BookingActivityLog } from '../../types'
import { formatDateTime, formatStatus } from '../../utils/format'

const props = defineProps<{
  booking: Booking | null
  logs?: BookingActivityLog[]
  logsLoading?: boolean
  open: boolean
  showActions?: boolean
  busy?: boolean
}>()

const emit = defineEmits<{
  close: []
  changeStatus: [status: string]
  reviewPayment: [action: 'approve' | 'reject', note?: string]
  updateProgress: [payload: { progress_percent: number; progress_note?: string; extended_until?: string; extension_note?: string }]
}>()

const reviewNote = ref('')
const progressPercent = ref(0)
const progressNote = ref('')
const extendedUntil = ref('')
const extensionNote = ref('')

const paymentLabel = computed(() => {
  if (!props.booking) return ''
  return (
    {
      unpaid: 'Chưa gửi bill / chưa thanh toán',
      proof_submitted: 'Đã gửi bill · chờ duyệt',
      paid: 'Đã duyệt thanh toán',
    }[props.booking.payment_status || ''] ?? (props.booking.payment_status || '—')
  )
})

const pricingLabel = computed(() => {
  if (!props.booking) return ''
  return props.booking.pricing_type === 'hourly' ? 'Theo giờ' : 'Theo trận'
})

const amountLabel = computed(() => {
  if (!props.booking) return ''
  const amount = new Intl.NumberFormat('vi-VN').format(props.booking.total_amount || 0)
  return `${amount} ${props.booking.currency || 'VND'}`
})

const proofUrl = computed(() => resolveMediaUrl(props.booking?.payment_proof_url))
const canConfirm = computed(() => props.booking?.payment_status === 'paid')
const canReviewPayment = computed(
  () =>
    Boolean(props.booking?.payment_proof_url) &&
    props.booking?.payment_status === 'proof_submitted',
)
/** Booking đã khoá hoàn toàn – không được thao tác thêm */
const isLocked = computed(() =>
  props.booking?.status === 'completed' || props.booking?.status === 'cancelled',
)
const progressLabel = computed(() => `${progressPercent.value}%`)

function statusTone(status: string) {
  return (
    {
      pending: 'border-amber-400/30 bg-amber-500/10 text-amber-100',
      confirmed: 'border-sky-400/30 bg-sky-500/10 text-sky-100',
      completed: 'border-emerald-400/30 bg-emerald-500/10 text-emerald-100',
      cancelled: 'border-rose-400/30 bg-rose-500/10 text-rose-100',
    }[status] ?? 'border-white/10 bg-white/5 text-slate-200'
  )
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && props.open) emit('close')
}

watch(
  () => props.open,
  (isOpen) => {
    document.body.style.overflow = isOpen ? 'hidden' : ''
    if (isOpen) {
      reviewNote.value = ''
      progressPercent.value = props.booking?.progress_percent ?? 0
      progressNote.value = props.booking?.progress_note ?? ''
      extendedUntil.value = props.booking?.extended_until ? props.booking.extended_until.slice(0, 16) : ''
      extensionNote.value = props.booking?.extension_note ?? ''
    }
  },
)

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="booking-detail">
      <div
        v-if="open && booking"
        class="fixed inset-0 z-[80] flex items-end justify-center bg-slate-950/70 p-3 backdrop-blur-sm sm:items-center sm:p-6"
        @click.self="emit('close')"
      >
        <section
          class="max-h-[92vh] w-full max-w-xl overflow-y-auto rounded-[1.75rem] border border-white/10 bg-[#14102a] shadow-2xl"
          role="dialog"
          aria-modal="true"
          aria-labelledby="booking-detail-title"
        >
          <header class="sticky top-0 z-10 flex items-start justify-between gap-4 border-b border-white/8 bg-[#14102a]/95 px-5 py-4 backdrop-blur">
            <div class="min-w-0">
              <p class="text-xs uppercase tracking-[0.28em] text-fuchsia-300/80">Chi tiết booking</p>
              <h2 id="booking-detail-title" class="mt-2 truncate text-xl font-semibold text-white">
                {{ booking.guest_name || booking.customer_email || 'Khách đặt lịch' }}
              </h2>
              <span
                class="mt-3 inline-flex rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.2em]"
                :class="statusTone(booking.status)"
              >
                {{ formatStatus(booking.status) }}
              </span>
            </div>
            <button
              type="button"
              class="shrink-0 rounded-full border border-white/10 px-3 py-1.5 text-sm text-slate-300 transition hover:bg-white/5"
              @click="emit('close')"
            >
              Đóng
            </button>
          </header>

          <div class="space-y-5 px-5 py-5">
            <div class="grid gap-3 sm:grid-cols-2">
              <div class="rounded-2xl border border-white/8 bg-white/4 p-4">
                <p class="text-[11px] uppercase tracking-[0.2em] text-slate-400">Thời gian</p>
                <p class="mt-2 text-sm font-medium text-white">{{ formatDateTime(booking.scheduled_at) }}</p>
              </div>
              <div class="rounded-2xl border border-white/8 bg-white/4 p-4">
                <p class="text-[11px] uppercase tracking-[0.2em] text-slate-400">Gói dịch vụ</p>
                <p class="mt-2 text-sm font-medium text-white">
                  {{ pricingLabel }} × {{ booking.quantity || 1 }}
                </p>
              </div>
              <div class="rounded-2xl border border-white/8 bg-white/4 p-4">
                <p class="text-[11px] uppercase tracking-[0.2em] text-slate-400">Tổng tiền</p>
                <p class="mt-2 text-sm font-medium text-violet-200">{{ amountLabel }}</p>
              </div>
              <div class="rounded-2xl border border-white/8 bg-white/4 p-4">
                <p class="text-[11px] uppercase tracking-[0.2em] text-slate-400">Thanh toán</p>
                <p class="mt-2 text-sm font-medium text-white">{{ paymentLabel }}</p>
              </div>
            </div>

            <div class="rounded-2xl border border-white/8 bg-white/4 p-4">
              <p class="text-[11px] uppercase tracking-[0.2em] text-slate-400">Liên hệ khách</p>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3">
                  <dt class="text-slate-400">Email</dt>
                  <dd class="text-right text-slate-100">{{ booking.customer_email || '—' }}</dd>
                </div>
                <div class="flex justify-between gap-3">
                  <dt class="text-slate-400">SĐT</dt>
                  <dd class="text-right text-slate-100">{{ booking.guest_phone || '—' }}</dd>
                </div>
                <div class="flex justify-between gap-3">
                  <dt class="text-slate-400">Zalo</dt>
                  <dd class="text-right text-slate-100">{{ booking.guest_zalo || '—' }}</dd>
                </div>
                <div class="flex justify-between gap-3">
                  <dt class="text-slate-400">Messenger</dt>
                  <dd class="text-right text-slate-100">{{ booking.guest_messenger || '—' }}</dd>
                </div>
              </dl>
            </div>

            <div class="rounded-2xl border border-white/8 bg-white/4 p-4">
              <p class="text-[11px] uppercase tracking-[0.2em] text-slate-400">Ghi chú đặt lịch</p>
              <p class="mt-2 text-sm leading-6 text-slate-200">
                {{ booking.notes || 'Không có ghi chú.' }}
              </p>
            </div>

            <div class="rounded-2xl border border-white/8 bg-white/4 p-4">
              <div class="flex items-center justify-between gap-3">
                <p class="text-[11px] uppercase tracking-[0.2em] text-slate-400">Tiến độ thực hiện</p>
                <span class="rounded-full border border-white/10 px-3 py-1 text-xs font-semibold text-white">{{ progressLabel }}</span>
              </div>
              <div class="mt-4">
                <input v-model.number="progressPercent" type="range" min="0" max="100" class="w-full" />
              </div>
              <textarea
                v-model="progressNote"
                rows="3"
                maxlength="2000"
                placeholder="Đã làm tới đâu, còn chờ gì, note nội bộ..."
                class="mt-3 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none placeholder:text-slate-500"
              />
              <div class="mt-4 grid gap-3 sm:grid-cols-2">
                <div>
                  <label class="mb-2 block text-xs uppercase tracking-[0.2em] text-slate-400">Gia hạn đến</label>
                  <input
                    v-model="extendedUntil"
                    type="datetime-local"
                    class="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none"
                  />
                </div>
                <div>
                  <label class="mb-2 block text-xs uppercase tracking-[0.2em] text-slate-400">Ghi chú gia hạn</label>
                  <input
                    v-model="extensionNote"
                    type="text"
                    maxlength="2000"
                    placeholder="Khách xin thêm 2 ngày, chờ duyệt..."
                    class="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none placeholder:text-slate-500"
                  />
                </div>
              </div>
              <div class="mt-4 flex justify-end">
                <button
                  class="btn-primary"
                  type="button"
                  :disabled="busy"
                  @click="
                    emit('updateProgress', {
                      progress_percent: progressPercent,
                      progress_note: progressNote || undefined,
                      extended_until: extendedUntil || undefined,
                      extension_note: extensionNote || undefined,
                    })
                  "
                >
                  Lưu tiến độ
                </button>
              </div>
            </div>

            <div v-if="booking.payment_code || booking.payment_qr_url" class="rounded-2xl border border-white/8 bg-white/4 p-4">
              <p class="text-[11px] uppercase tracking-[0.2em] text-slate-400">Thông tin QR</p>
              <p v-if="booking.payment_code" class="mt-2 text-sm text-slate-200">
                Mã: <span class="font-medium text-white">{{ booking.payment_code }}</span>
              </p>
              <img
                v-if="booking.payment_qr_url"
                :src="booking.payment_qr_url"
                alt="QR thanh toán"
                class="mt-3 h-36 w-36 rounded-2xl border border-white/10 bg-white p-2"
              />
            </div>

            <div class="rounded-2xl border border-white/8 bg-white/4 p-4">
              <p class="text-[11px] uppercase tracking-[0.2em] text-slate-400">Bill chuyển khoản</p>
              <p v-if="booking.payment_proof_note" class="mt-2 text-sm text-amber-100">
                {{ booking.payment_proof_note }}
              </p>
              <div v-if="proofUrl" class="mt-3">
                <a :href="proofUrl" target="_blank" rel="noopener noreferrer">
                  <img
                    :src="proofUrl"
                    alt="Bill chuyển khoản"
                    class="max-h-72 w-full rounded-2xl border border-white/10 object-contain bg-black/20"
                  />
                </a>
              </div>
              <p v-else class="mt-2 text-sm text-slate-400">Khách chưa gửi bill.</p>

              <div v-if="canReviewPayment" class="mt-4 space-y-3">
                <input
                  v-model="reviewNote"
                  type="text"
                  maxlength="500"
                  placeholder="Ghi chú duyệt / lý do từ chối (tuỳ chọn)"
                  class="h-10 w-full rounded-xl border border-white/10 bg-white/5 px-3 text-sm text-white outline-none placeholder:text-slate-500"
                />
                <div class="grid grid-cols-2 gap-2">
                  <button
                    class="btn-primary"
                    type="button"
                    :disabled="busy"
                    @click="emit('reviewPayment', 'approve', reviewNote)"
                  >
                    Duyệt khớp & xác nhận
                  </button>
                  <button
                    class="btn-secondary"
                    type="button"
                    :disabled="busy"
                    @click="emit('reviewPayment', 'reject', reviewNote)"
                  >
                    Bill không khớp
                  </button>
                </div>
              </div>
            </div>

            <!-- Status Actions -->
            <div v-if="showActions" class="rounded-2xl border border-white/8 bg-white/4 p-4">
              <p class="text-[11px] uppercase tracking-[0.2em] text-slate-400">Cập nhật trạng thái</p>

              <!-- Locked banner -->
              <div
                v-if="isLocked"
                class="mt-3 flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2.5"
              >
                <span class="text-base">{{ booking?.status === 'completed' ? '✅' : '⛔' }}</span>
                <p class="text-xs text-slate-300">
                  Booking đã <strong class="text-white">{{ booking?.status === 'completed' ? 'hoàn thành' : 'bị huỷ' }}</strong> —
                  không thể thay đổi thêm.
                </p>
              </div>

              <!-- Active action buttons -->
              <template v-else>
                <p v-if="!canConfirm" class="mt-2 text-xs text-amber-200">
                  Chỉ xác nhận sau khi đã duyệt bill chuyển khoản khớp.
                </p>
                <div class="mt-3 grid grid-cols-2 gap-2">
                  <!-- pending → confirmed -->
                  <button
                    v-if="booking?.status === 'pending'"
                    class="btn-secondary"
                    type="button"
                    :disabled="busy || !canConfirm"
                    @click="emit('changeStatus', 'confirmed')"
                  >
                    Xác nhận
                  </button>
                  <!-- confirmed → completed -->
                  <button
                    v-if="booking?.status === 'confirmed'"
                    class="btn-secondary"
                    type="button"
                    :disabled="busy"
                    @click="emit('changeStatus', 'completed')"
                  >
                    Hoàn thành
                  </button>
                  <!-- any active → cancelled -->
                  <button
                    class="btn-secondary col-span-2 border-rose-500/20 text-rose-300 hover:bg-rose-500/10"
                    type="button"
                    :disabled="busy"
                    @click="emit('changeStatus', 'cancelled')"
                  >
                    Huỷ booking
                  </button>
                </div>
              </template>
            </div>

            <div class="rounded-2xl border border-white/8 bg-white/4 p-4 text-xs text-slate-400">
              <p>Mã booking: {{ booking.id }}</p>
              <p class="mt-1">Nguồn: {{ booking.source || 'system' }}</p>
              <p v-if="booking.extension_count" class="mt-1">Số lần gia hạn: {{ booking.extension_count }}</p>
              <p class="mt-1">Tạo lúc: {{ formatDateTime(booking.created_at) }}</p>
              <p class="mt-1">Cập nhật: {{ formatDateTime(booking.updated_at) }}</p>
            </div>

            <div class="rounded-2xl border border-white/8 bg-white/4 p-4">
              <div class="flex items-center justify-between gap-3">
                <p class="text-[11px] uppercase tracking-[0.2em] text-slate-400">Nhật ký hoạt động</p>
                <span class="text-xs text-slate-500">{{ logs?.length ?? 0 }} mục</span>
              </div>
              <p class="mt-2 text-sm text-slate-400">
                Ghi lại các thao tác quan trọng để dễ dò lại khi có lỗi hoặc phát sinh.
              </p>
              <div v-if="logsLoading" class="mt-4 text-sm text-slate-400">Đang tải log...</div>
              <div v-else-if="!logs?.length" class="mt-4 text-sm text-slate-400">Chưa có log nào.</div>
              <div v-else class="mt-4 space-y-3">
                <article
                  v-for="item in logs"
                  :key="item.id"
                  class="rounded-xl border border-white/8 bg-black/10 px-3 py-3"
                >
                  <div class="flex flex-wrap items-center justify-between gap-2">
                    <p class="text-sm font-medium text-white">{{ item.message }}</p>
                    <span class="text-xs text-slate-500">{{ formatDateTime(item.created_at) }}</span>
                  </div>
                  <p class="mt-1 text-xs uppercase tracking-[0.16em] text-violet-200">
                    {{ item.actor_role || 'system' }} · {{ item.action }}
                  </p>
                  <div v-if="item.metadata" class="mt-2 rounded-lg bg-white/5 px-3 py-2 text-xs text-slate-300">
                    <pre class="whitespace-pre-wrap break-words">{{ JSON.stringify(item.metadata, null, 2) }}</pre>
                  </div>
                </article>
              </div>
            </div>
          </div>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.booking-detail-enter-active,
.booking-detail-leave-active {
  transition: opacity 0.18s ease;
}
.booking-detail-enter-active section,
.booking-detail-leave-active section {
  transition: transform 0.18s ease, opacity 0.18s ease;
}
.booking-detail-enter-from,
.booking-detail-leave-to {
  opacity: 0;
}
.booking-detail-enter-from section,
.booking-detail-leave-to section {
  opacity: 0;
  transform: translateY(12px) scale(0.98);
}
</style>
