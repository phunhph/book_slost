<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import ProfilePageRenderer from '@/components/profile/ProfilePageRenderer.vue'
import { getErrorMessage } from '@/lib/errors'
import { getPublicProfile } from '@/services/public'
import { useToastStore } from '@/stores/toast'
import type { UserProfile } from '@/types/profile'

const route = useRoute()
const toast = useToastStore()
const emit = defineEmits<{
  openAuth: [mode: 'login' | 'register']
}>()

const profile = ref<UserProfile | null>(null)
const isLoading = ref(true)
const loadFailed = ref(false)
const loadError = ref('')

async function loadProfile() {
  const username = String(route.params.username ?? '')
  if (!username) {
    loadFailed.value = true
    loadError.value = 'Thiếu tên creator trên đường dẫn.'
    toast.error(loadError.value)
    isLoading.value = false
    return
  }

  isLoading.value = true
  loadFailed.value = false
  loadError.value = ''

  try {
    profile.value = await getPublicProfile(username)
  } catch (error) {
    loadFailed.value = true
    loadError.value = getErrorMessage(error, 'Không tải được hồ sơ creator.')
    toast.error(loadError.value)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadProfile)
watch(() => route.params.username, loadProfile)
</script>

<template>
  <section v-if="isLoading" class="page-container py-10">
    <div class="min-h-[50vh] animate-pulse rounded-2xl border border-white/10 bg-white/6"></div>
  </section>

  <section v-else-if="loadFailed" class="page-container py-10">
    <div class="rounded-2xl border border-rose-400/20 bg-rose-500/10 p-6 text-rose-100">
      {{ loadError || 'Không tải được trang creator này.' }}
    </div>
  </section>

  <section v-else-if="profile">
    <ProfilePageRenderer :profile="profile" @open-auth="emit('openAuth', 'login')" />
  </section>
</template>
