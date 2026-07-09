<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import { getErrorMessage } from '../utils/errors'

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
    toast.error(getErrorMessage(oauthError, 'Đăng nhập Google thất bại.'))
    return
  }

  if (!accessToken) {
    hasError.value = true
    toast.error('Google không trả về access token.')
    return
  }

  try {
    auth.acceptOAuthToken(accessToken)
    await auth.finalizeOAuth()
    await router.replace('/dashboard')
  } catch (error) {
    hasError.value = true
    toast.error(getErrorMessage(error, 'Đăng nhập Google thất bại.'))
  }
})
</script>

<template>
  <div class="flex min-h-screen items-center justify-center px-4">
    <div class="glass-panel w-full max-w-xl rounded-[2rem] p-8 text-center">
      <template v-if="!hasError">
        <p class="text-sm uppercase tracking-[0.35em] text-violet-300/85">Google OAuth</p>
        <h1 class="mt-4 text-3xl font-semibold text-white">Đang hoàn tất đăng nhập...</h1>
        <p class="mt-3 text-slate-300">
          Hệ thống đang xác minh tài khoản Google và chuẩn bị không gian làm việc KOL.
        </p>
      </template>

      <template v-else>
        <p class="text-sm uppercase tracking-[0.35em] text-rose-300/85">Lỗi đăng nhập</p>
        <h1 class="mt-4 text-3xl font-semibold text-white">Không thể hoàn tất đăng nhập Google</h1>
        <p class="mt-3 text-slate-300">Kiểm tra thông báo ở góc trên bên phải.</p>
        <RouterLink class="btn-primary mt-6 inline-flex" to="/login">Quay lại đăng nhập</RouterLink>
      </template>
    </div>
  </div>
</template>
