<script setup lang="ts">
import type { UserProfile } from '@/types/profile'

defineProps<{
  profile: UserProfile
  title?: string
  subtitle?: string
}>()
</script>

<template>
  <section class="profile-section">
    <!-- Preview of CTA Card -->
    <div class="relative overflow-hidden rounded-3xl border border-white/12 bg-white/5 p-6 sm:p-8 text-center flex flex-col items-center">
      <p class="profile-section__label">Đặt lịch (Bản xem trước)</p>
      <h2 class="profile-section__title text-2xl font-bold mt-2 text-white">{{ title ?? 'Đặt lịch chơi cùng' }}</h2>
      <p v-if="subtitle" class="mt-2 text-sm opacity-80 max-w-md">{{ subtitle }}</p>

      <div class="mt-4 text-xs text-violet-300 bg-violet-500/10 px-4 py-2 rounded-xl border border-violet-500/20 max-w-md">
        Khách hàng sẽ nhấp vào nút dưới đây để mở form đặt lịch trong một Popup Modal, thay vì hiển thị trực tiếp ở chân trang như trước.
      </div>
      
      <button 
        type="button"
        disabled
        class="mt-6 px-8 py-3.5 rounded-full font-bold text-slate-950 opacity-80 cursor-not-allowed"
        :style="{ 
          background: profile.primary_color || '#8b5cf6', 
          boxShadow: `0 10px 30px ${profile.primary_color || '#8b5cf6'}40` 
        }"
      >
        Đặt lịch ngay
      </button>
    </div>
  </section>
</template>
