<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { googleOAuthUrl } from '../services/api'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'

const auth = useAuthStore()
const toast = useToastStore()
const route = useRoute()
const router = useRouter()

const email = ref('')
const password = ref('')

const redirectTarget = computed(() => {
  return typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
})

async function submit() {
  try {
    await auth.login(email.value, password.value)
    await router.push(redirectTarget.value)
  } catch (error) {
    if (axios.isAxiosError(error) && !error.response) {
      toast.error(
        'Cannot reach API server. Start backend on port 8000 or open this app via http://localhost:3002 instead of a LAN IP.',
      )
      return
    }

    const message = error instanceof Error ? error.message : 'Unable to sign in.'
    toast.error(message)
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center px-4 py-8 sm:py-10">
    <div class="grid w-full max-w-6xl gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <section class="glass-panel rounded-[2rem] p-6 sm:p-8 lg:p-10">
        <p class="text-sm uppercase tracking-[0.35em] text-fuchsia-300/85">Violet Studio</p>
        <h1 class="mt-4 max-w-xl text-3xl font-semibold leading-tight text-white sm:text-4xl lg:text-5xl">
          Professional creator operations for your KOL workflow.
        </h1>
        <p class="mt-5 max-w-2xl text-base text-slate-300">
          Track new collaborations, manage your calendar, update your public presence, and stay
          on top of every booking from one creator-focused workspace.
        </p>

        <div class="mt-8 grid gap-4 md:grid-cols-3">
          <div class="rounded-3xl border border-white/8 bg-white/5 p-5">
            <p class="text-sm text-slate-300">Bookings in motion</p>
            <p class="mt-3 text-3xl font-semibold text-white">24/7</p>
          </div>
          <div class="rounded-3xl border border-white/8 bg-white/5 p-5">
            <p class="text-sm text-slate-300">Creator-first views</p>
            <p class="mt-3 text-3xl font-semibold text-white">6</p>
          </div>
          <div class="rounded-3xl border border-white/8 bg-white/5 p-5">
            <p class="text-sm text-slate-300">Workspace theme</p>
            <p class="mt-3 text-3xl font-semibold text-white">Violet</p>
          </div>
        </div>
      </section>

      <section class="glass-panel rounded-[2rem] p-8 lg:p-10">
        <p class="text-sm uppercase tracking-[0.35em] text-violet-300/85">Sign in</p>
        <h2 class="mt-3 text-3xl font-semibold text-white">Access your KOL dashboard</h2>
        <p class="mt-3 text-sm text-slate-300">
          Log in with your KOL account credentials or continue with Google.
        </p>

        <form class="mt-8 space-y-4" @submit.prevent="submit">
          <div>
            <label class="mb-2 block text-sm text-slate-300" for="email">Email</label>
            <input id="email" v-model="email" class="field" type="email" autocomplete="email" required />
          </div>

          <div>
            <label class="mb-2 block text-sm text-slate-300" for="password">Password</label>
            <input
              id="password"
              v-model="password"
              class="field"
              type="password"
              autocomplete="current-password"
              required
            />
          </div>

          <button class="btn-primary w-full" type="submit" :disabled="auth.loading">
            {{ auth.loading ? 'Signing in...' : 'Login with email' }}
          </button>
        </form>

        <div class="my-6 flex items-center gap-4">
          <div class="h-px flex-1 bg-white/10"></div>
          <span class="text-xs uppercase tracking-[0.25em] text-slate-400">or</span>
          <div class="h-px flex-1 bg-white/10"></div>
        </div>

        <a :href="googleOAuthUrl" class="btn-secondary flex w-full items-center justify-center gap-3">
          <span>Continue with Google</span>
        </a>
      </section>
    </div>
  </div>
</template>
