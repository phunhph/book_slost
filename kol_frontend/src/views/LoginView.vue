<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { googleOAuthUrl } from '../services/api'
import {
  clearRememberedCredentials,
  readRememberedCredentials,
  saveRememberedCredentials,
  useAuthStore,
} from '../stores/auth'
import { useToastStore } from '../stores/toast'
import { getErrorMessage } from '../utils/errors'

type FieldName = 'email' | 'password'

const auth = useAuthStore()
const toast = useToastStore()
const route = useRoute()
const router = useRouter()

const remembered = readRememberedCredentials()
const email = ref(remembered?.email || '')
const password = ref(remembered?.password || '')
const rememberMe = ref(Boolean(remembered))
const fieldErrors = reactive<Partial<Record<FieldName, string>>>({})
const touched = reactive<Partial<Record<FieldName, boolean>>>({})

const redirectTarget = computed(() => {
  return typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
})

function fieldClass(field: FieldName) {
  return ['field', touched[field] && fieldErrors[field] ? 'field--error' : '']
}

function validateField(field: FieldName): string {
  let message = ''
  if (field === 'email') {
    const value = email.value.trim()
    if (!value) message = 'Vui lòng nhập email.'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) message = 'Email không hợp lệ.'
  }
  if (field === 'password') {
    if (!password.value) message = 'Vui lòng nhập mật khẩu.'
    else if (password.value.length < 8) message = 'Mật khẩu tối thiểu 8 ký tự.'
  }
  if (message) fieldErrors[field] = message
  else delete fieldErrors[field]
  return message
}

function markTouched(field: FieldName) {
  touched[field] = true
  validateField(field)
}

function validateForm() {
  let ok = true
  for (const field of ['email', 'password'] as FieldName[]) {
    touched[field] = true
    if (validateField(field)) ok = false
  }
  return ok
}

async function submit() {
  if (!validateForm()) {
    toast.error('Vui lòng sửa các ô đang báo lỗi.')
    return
  }

  try {
    await auth.login(email.value.trim(), password.value)
    if (rememberMe.value) {
      saveRememberedCredentials(email.value.trim(), password.value)
    } else {
      clearRememberedCredentials()
    }
    await router.push(redirectTarget.value)
  } catch (error) {
    toast.error(getErrorMessage(error, 'Không thể đăng nhập.'))
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center px-4 py-8 sm:py-10">
    <div class="grid w-full max-w-6xl gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <section class="glass-panel rounded-[2rem] p-6 sm:p-8 lg:p-10">
        <p class="text-sm uppercase tracking-[0.35em] text-fuchsia-300/85">Violet Studio</p>
        <h1 class="mt-4 max-w-xl text-3xl font-semibold leading-tight text-white sm:text-4xl lg:text-5xl">
          Vận hành creator chuyên nghiệp cho quy trình KOL của bạn.
        </h1>
        <p class="mt-5 max-w-2xl text-base text-slate-300">
          Theo dõi hợp tác mới, quản lý lịch, cập nhật hiện diện công khai và nắm mọi booking trong một không gian dành cho creator.
        </p>

        <div class="mt-8 grid gap-4 md:grid-cols-3">
          <div class="rounded-3xl border border-white/8 bg-white/5 p-5">
            <p class="text-sm text-slate-300">Booking liên tục</p>
            <p class="mt-3 text-3xl font-semibold text-white">24/7</p>
          </div>
          <div class="rounded-3xl border border-white/8 bg-white/5 p-5">
            <p class="text-sm text-slate-300">Góc nhìn creator</p>
            <p class="mt-3 text-3xl font-semibold text-white">6</p>
          </div>
          <div class="rounded-3xl border border-white/8 bg-white/5 p-5">
            <p class="text-sm text-slate-300">Theme workspace</p>
            <p class="mt-3 text-3xl font-semibold text-white">Violet</p>
          </div>
        </div>
      </section>

      <section class="glass-panel rounded-[2rem] p-8 lg:p-10">
        <p class="text-sm uppercase tracking-[0.35em] text-violet-300/85">Đăng nhập</p>
        <h2 class="mt-3 text-3xl font-semibold text-white">Vào bảng điều khiển KOL</h2>
        <p class="mt-3 text-sm text-slate-300">
          Đăng nhập bằng tài khoản KOL hoặc tiếp tục với Google.
        </p>

        <form class="mt-8 space-y-4" novalidate @submit.prevent="submit">
          <div>
            <label class="mb-2 block text-sm text-slate-300" for="email">Email *</label>
            <input
              id="email"
              v-model="email"
              :class="fieldClass('email')"
              type="email"
              autocomplete="email"
              @blur="markTouched('email')"
              @input="validateField('email')"
            />
            <p v-if="touched.email && fieldErrors.email" class="field-error">{{ fieldErrors.email }}</p>
          </div>

          <div>
            <label class="mb-2 block text-sm text-slate-300" for="password">Mật khẩu *</label>
            <input
              id="password"
              v-model="password"
              :class="fieldClass('password')"
              type="password"
              autocomplete="current-password"
              @blur="markTouched('password')"
              @input="validateField('password')"
            />
            <p v-if="touched.password && fieldErrors.password" class="field-error">{{ fieldErrors.password }}</p>
          </div>

          <label class="flex items-center gap-3 text-sm text-slate-300">
            <input v-model="rememberMe" class="h-4 w-4 rounded border-white/20 bg-white/10" type="checkbox" />
            <span>Ghi nhớ email & mật khẩu</span>
          </label>

          <button class="btn-primary w-full" type="submit" :disabled="auth.loading">
            {{ auth.loading ? 'Đang đăng nhập...' : 'Đăng nhập bằng email' }}
          </button>
        </form>

        <div class="my-6 flex items-center gap-4">
          <div class="h-px flex-1 bg-white/10"></div>
          <span class="text-xs uppercase tracking-[0.25em] text-slate-400">hoặc</span>
          <div class="h-px flex-1 bg-white/10"></div>
        </div>

        <a :href="googleOAuthUrl" class="btn-secondary flex w-full items-center justify-center gap-3">
          <span>Tiếp tục với Google</span>
        </a>
      </section>
    </div>
  </div>
</template>
