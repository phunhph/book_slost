<script setup lang="ts">
import BookingForm from '@/components/profile/BookingForm.vue'
import type { UserProfile } from '@/types/profile'

defineProps<{
  profile: UserProfile
  title?: string
  subtitle?: string
}>()

const emit = defineEmits<{
  requestAuth: []
}>()
</script>

<template>
  <BookingForm
      :kol-profile="profile"
      :title="title"
      :subtitle="subtitle"
      @request-auth="emit('requestAuth')"
    />
</template>
