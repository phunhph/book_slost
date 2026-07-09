<script setup lang="ts">
import { ref } from 'vue'
import BookingForm from '@/components/profile/BookingForm.vue'
import type { UserProfile } from '@/types/profile'

const props = defineProps<{
  profile: UserProfile
  title?: string
  subtitle?: string
}>()

const emit = defineEmits<{
  requestAuth: []
}>()

const isModalOpen = ref(false)

function openModal() {
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
}
</script>

<template>
  <section class="profile-section" id="booking-section">
    <!-- Call-to-Action Card -->
    <div class="relative overflow-hidden rounded-3xl border border-white/12 bg-white/5 p-6 sm:p-8 text-center flex flex-col items-center">
      <div 
        class="absolute -top-10 -left-10 w-40 h-40 rounded-full blur-[80px]"
        :style="{ backgroundColor: profile.primary_color + '20' }"
      />
      <div 
        class="absolute -bottom-10 -right-10 w-40 h-40 rounded-full blur-[80px]"
        :style="{ backgroundColor: profile.primary_color + '20' }"
      />

      <p class="profile-section__label">Đặt lịch</p>
      <h2 class="profile-section__title text-2xl font-bold mt-2 text-white">{{ title ?? 'Đặt lịch chơi cùng' }}</h2>
      <p v-if="subtitle" class="mt-2 text-sm opacity-80 max-w-md">{{ subtitle }}</p>
      
      <!-- Current Pricing Indicator -->
      <div class="mt-6 flex flex-wrap justify-center gap-4 text-xs bg-black/30 border border-white/8 rounded-2xl px-5 py-3">
        <div>
          Theo trận: <strong class="text-white">{{ new Intl.NumberFormat('vi-VN').format(profile.price_per_match || 0) }} {{ profile.currency || 'VND' }}</strong>
        </div>
        <div class="w-px h-4 bg-white/10 hidden sm:block"></div>
        <div>
          Theo giờ: <strong class="text-white">{{ new Intl.NumberFormat('vi-VN').format(profile.price_per_hour || 0) }} {{ profile.currency || 'VND' }}</strong>
        </div>
      </div>

      <!-- Action Button -->
      <button 
        type="button"
        @click="openModal"
        class="mt-6 px-8 py-3.5 rounded-full font-bold text-slate-950 transition hover:scale-[1.02] active:scale-[0.98] cursor-pointer shadow-lg"
        :style="{ 
          background: profile.primary_color || '#8b5cf6', 
          boxShadow: `0 10px 30px ${profile.primary_color || '#8b5cf6'}40` 
        }"
      >
        Đặt lịch ngay
      </button>
    </div>

    <!-- Booking Modal -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div 
          v-if="isModalOpen" 
          class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/75 backdrop-blur-md"
          @click.self="closeModal"
        >
          <div class="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-[2rem] border border-white/10 bg-[#0f172a] p-6 shadow-2xl custom-scrollbar">
            <!-- Close Modal Button -->
            <button 
              type="button"
              @click="closeModal" 
              class="absolute top-4 right-4 text-slate-400 hover:text-white border border-white/10 bg-white/5 hover:bg-white/10 rounded-full px-3 py-1.5 text-xs font-semibold transition cursor-pointer"
            >
              Đóng
            </button>

            <!-- Embedded Booking Form -->
            <div class="mt-4">
              <BookingForm
                :kol-profile="profile"
                :title="title"
                :subtitle="subtitle"
                @request-auth="emit('requestAuth'); closeModal()"
                @success="closeModal"
              />
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 999px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}
.modal-fade-enter-active > div,
.modal-fade-leave-active > div {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-from > div,
.modal-fade-leave-to > div {
  opacity: 0;
  transform: scale(0.96);
}
</style>
