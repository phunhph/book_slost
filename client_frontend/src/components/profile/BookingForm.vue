<script setup lang="ts">
import { computed, reactive, watch } from "vue";

import { createBooking } from "@/services/bookings";
import { useAuthStore } from "@/stores/auth";
import { useToastStore } from "@/stores/toast";
import type { UserProfile } from "@/types/profile";

const props = defineProps<{
  kolProfile: UserProfile;
  title?: string;
  subtitle?: string;
}>();

const emit = defineEmits<{
  requestAuth: [];
}>();

const authStore = useAuthStore();
const toast = useToastStore();

const form = reactive({
  guest_name: "",
  guest_phone: "",
  guest_zalo: "",
  guest_messenger: "",
  scheduled_at: "",
  notes: "",
});

const state = reactive({
  isSubmitting: false,
});

const isAuthenticated = computed(() => authStore.isAuthenticated);
const customerProfile = computed(() => authStore.userProfile);

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

async function submitBooking() {
  if (!form.guest_phone.trim()) {
    toast.error("Phone number is required.");
    return;
  }

  if (!form.scheduled_at) {
    toast.error("Please choose a date and time.");
    return;
  }

  state.isSubmitting = true;

  try {
    const response = await createBooking(
      {
        kol_user_id: props.kolProfile.user_id,
        scheduled_at: new Date(form.scheduled_at).toISOString(),
        notes: form.notes.trim() || undefined,
        guest_name: form.guest_name.trim() || undefined,
        guest_phone: form.guest_phone.trim(),
        guest_zalo: form.guest_zalo.trim() || undefined,
        guest_messenger: form.guest_messenger.trim() || undefined,
      },
      authStore.accessToken ?? undefined,
    );

    toast.success(`Booking request submitted with status: ${response.status}.`);
    form.scheduled_at = "";
    form.notes = "";
  } catch (error) {
    toast.error(error instanceof Error ? error.message : "Booking failed.");
  } finally {
    state.isSubmitting = false;
  }
}
</script>

<template>
  <section class="profile-section" id="booking-section">
    <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <p class="profile-section__label">Booking</p>
        <h2 class="profile-section__title">{{ title ?? 'Request a campaign' }}</h2>
        <p v-if="subtitle" class="profile-section__body !mt-2 !opacity-80">{{ subtitle }}</p>
      </div>
      <button
        v-if="!isAuthenticated"
        class="rounded-full border border-white/14 px-4 py-2 text-sm font-medium transition hover:bg-white/8"
        type="button"
        @click="emit('requestAuth')"
      >
        Login for autofill
      </button>
    </div>

    <p class="profile-section__body !mt-4">
      {{ isAuthenticated ? 'Your contact details are prefilled from your customer profile. You can still adjust them before sending.' : 'Guests can book directly. Phone is required so the creator can follow up quickly.' }}
    </p>

    <form class="mt-6 grid gap-4 sm:grid-cols-2" @submit.prevent="submitBooking">
      <label class="text-sm">
        <span class="mb-2 block opacity-80">Guest name</span>
        <input v-model="form.guest_name" class="w-full rounded-2xl border border-white/12 bg-black/15 px-4 py-3 outline-none transition placeholder:text-slate-400 focus:border-sky-300" placeholder="Your name" type="text" />
      </label>

      <label class="text-sm">
        <span class="mb-2 block opacity-80">Phone *</span>
        <input v-model="form.guest_phone" class="w-full rounded-2xl border border-white/12 bg-black/15 px-4 py-3 outline-none transition placeholder:text-slate-400 focus:border-sky-300" placeholder="Phone number" type="tel" required />
      </label>

      <label class="text-sm">
        <span class="mb-2 block opacity-80">Zalo</span>
        <input v-model="form.guest_zalo" class="w-full rounded-2xl border border-white/12 bg-black/15 px-4 py-3 outline-none transition placeholder:text-slate-400 focus:border-sky-300" placeholder="Zalo contact" type="text" />
      </label>

      <label class="text-sm">
        <span class="mb-2 block opacity-80">Messenger</span>
        <input v-model="form.guest_messenger" class="w-full rounded-2xl border border-white/12 bg-black/15 px-4 py-3 outline-none transition placeholder:text-slate-400 focus:border-sky-300" placeholder="Messenger profile" type="text" />
      </label>

      <label class="text-sm sm:col-span-2">
        <span class="mb-2 block opacity-80">Scheduled at *</span>
        <input v-model="form.scheduled_at" class="w-full rounded-2xl border border-white/12 bg-black/15 px-4 py-3 outline-none transition focus:border-sky-300" type="datetime-local" required />
      </label>

      <label class="text-sm sm:col-span-2">
        <span class="mb-2 block opacity-80">Notes</span>
        <textarea v-model="form.notes" class="min-h-32 w-full rounded-2xl border border-white/12 bg-black/15 px-4 py-3 outline-none transition placeholder:text-slate-400 focus:border-sky-300" placeholder="Campaign brief, budget range, target timeline, deliverables..." />
      </label>

      <button
        class="sm:col-span-2 rounded-2xl px-5 py-3 text-sm font-semibold text-slate-950 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
        type="submit"
        :disabled="state.isSubmitting"
        :style="{ background: kolProfile.primary_color }"
      >
        {{ state.isSubmitting ? 'Submitting request...' : 'Send booking request' }}
      </button>
    </form>
  </section>
</template>
