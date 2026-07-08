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
    <p class="profile-section__label">Booking</p>
    <h2 class="profile-section__title">{{ title ?? 'Request a campaign' }}</h2>
    <p v-if="subtitle" class="profile-section__body !mt-2 !opacity-80">{{ subtitle }}</p>
    <div class="mt-5 grid gap-3 sm:grid-cols-2">
      <div class="h-11 rounded-xl border border-current/12 bg-black/8"></div>
      <div class="h-11 rounded-xl border border-current/12 bg-black/8"></div>
      <div class="h-11 rounded-xl border border-current/12 bg-black/8 sm:col-span-2"></div>
      <div class="h-24 rounded-xl border border-current/12 bg-black/8 sm:col-span-2"></div>
      <div class="h-11 rounded-xl sm:col-span-2" :style="{ background: profile.primary_color }"></div>
    </div>
  </section>
</template>
