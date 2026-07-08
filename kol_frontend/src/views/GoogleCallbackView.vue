<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const toast = useToastStore()

const hasError = ref(false)

onMounted(async () => {
  const accessToken = typeof route.query.access_token === 'string' ? route.query.access_token : ''
  const oauthError = typeof route.query.error === 'string' ? route.query.error : ''

  if (oauthError) {
    hasError.value = true
    toast.error(oauthError)
    return
  }

  if (!accessToken) {
    hasError.value = true
    toast.error('Google login did not return an access token.')
    return
  }

  try {
    auth.acceptOAuthToken(accessToken)
    await auth.finalizeOAuth()
    await router.replace('/dashboard')
  } catch (error) {
    hasError.value = true
    toast.error(error instanceof Error ? error.message : 'Google login failed.')
  }
})
</script>

<template>
  <div class="flex min-h-screen items-center justify-center px-4">
    <div class="glass-panel w-full max-w-xl rounded-[2rem] p-8 text-center">
      <template v-if="!hasError">
        <p class="text-sm uppercase tracking-[0.35em] text-violet-300/85">Google OAuth</p>
        <h1 class="mt-4 text-3xl font-semibold text-white">Completing your sign in...</h1>
        <p class="mt-3 text-slate-300">
          We are verifying your Google account and preparing the KOL workspace.
        </p>
      </template>

      <template v-else>
        <p class="text-sm uppercase tracking-[0.35em] text-rose-300/85">Sign in error</p>
        <h1 class="mt-4 text-3xl font-semibold text-white">Unable to finish Google login</h1>
        <p class="mt-3 text-slate-300">Kiểm tra thông báo ở góc trên bên phải.</p>
        <RouterLink class="btn-primary mt-6 inline-flex" to="/login">Return to login</RouterLink>
      </template>
    </div>
  </div>
</template>
