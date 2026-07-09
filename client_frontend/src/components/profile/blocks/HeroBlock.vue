<script setup lang="ts">
import { computed } from 'vue'
import { contrastTextOn } from '@/lib/profileTheme'
import type { UserProfile } from '@/types/profile'
import { useAuthStore } from '@/stores/auth'

const props = withDefaults(
  defineProps<{
    profile: UserProfile
    showBio?: boolean
    showQuickContact?: boolean
    hideActions?: boolean
  }>(),
  { showBio: true, showQuickContact: true, hideActions: false },
)

const emit = defineEmits<{
  openAuth: []
}>()

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

const avatarClass = computed(() => {
  if (props.profile.avatar_style === 'circle') return 'rounded-full'
  if (props.profile.avatar_style === 'rounded') return 'rounded-2xl'
  return 'rounded-lg'
})

const buttonStyle = computed(() => {
  const primary = props.profile.primary_color
  const style = props.profile.button_style

  if (style === 'outline') {
    return { color: primary, background: 'transparent', borderColor: primary }
  }

  return {
    color: contrastTextOn(primary),
    background: primary,
    borderColor: primary,
    boxShadow: style === 'shadow' ? '0 12px 28px rgba(15, 23, 42, 0.22)' : undefined,
  }
})

const hasQuickContact = computed(
  () =>
    props.showQuickContact &&
    Boolean(props.profile.phone || props.profile.zalo || props.profile.messenger),
)
</script>

<template>
  <section class="profile-hero">
    <div class="flex flex-col gap-6 sm:flex-row sm:items-start">
      <div
        class="mx-auto h-28 w-28 shrink-0 overflow-hidden border border-current/15 bg-black/10 sm:mx-0 sm:h-32 sm:w-32"
        :class="avatarClass"
      >
        <img
          v-if="profile.avatar_url"
          :src="profile.avatar_url"
          :alt="profile.display_name ?? 'Avatar creator'"
          class="h-full w-full object-cover"
        />
        <div v-else class="flex h-full w-full items-center justify-center text-3xl font-semibold opacity-80">
          {{ (profile.display_name ?? profile.username ?? 'C').slice(0, 1).toUpperCase() }}
        </div>
      </div>

      <div class="min-w-0 flex-1 text-center sm:text-left">
        <p class="profile-public-eyebrow">Creator profile</p>
        <h1 class="profile-public-title">{{ profile.display_name ?? profile.username ?? 'Creator chưa đặt tên' }}</h1>
        <p class="profile-public-handle">@{{ profile.username ?? 'creator' }}</p>
        
        <!-- Pricing info at the top -->
        <div 
          v-if="profile.price_per_match || profile.price_per_hour"
          class="mt-3 flex flex-wrap justify-center sm:justify-start gap-2.5"
        >
          <span 
            v-if="profile.price_per_match"
            class="inline-flex items-center gap-1.5 rounded-xl border border-current/12 bg-current/5 px-3.5 py-1.5 text-xs font-semibold backdrop-blur-md text-current/80"
          >
            Theo trận:
            <strong class="font-bold text-current">
              {{ new Intl.NumberFormat('vi-VN').format(profile.price_per_match) }} {{ profile.currency || 'VND' }}
            </strong>
          </span>
          <span 
            v-if="profile.price_per_hour"
            class="inline-flex items-center gap-1.5 rounded-xl border border-current/12 bg-current/5 px-3.5 py-1.5 text-xs font-semibold backdrop-blur-md text-current/80"
          >
            Theo giờ:
            <strong class="font-bold text-current">
              {{ new Intl.NumberFormat('vi-VN').format(profile.price_per_hour) }} {{ profile.currency || 'VND' }}
            </strong>
          </span>
        </div>

        <p v-if="showBio && profile.bio" class="profile-public-bio profile-public-bio--compact mt-4">{{ profile.bio }}</p>

        <div v-if="hasQuickContact" class="profile-public-contacts justify-center sm:justify-start">
          <a v-if="profile.phone" class="profile-public-chip profile-public-chip--accent" :href="`tel:${profile.phone}`">
            <span class="profile-public-chip-label">Điện thoại</span>
            {{ profile.phone }}
          </a>
          <span v-if="profile.zalo" class="profile-public-chip">
            <span class="profile-public-chip-label">Zalo</span>
            {{ profile.zalo }}
          </span>
          <span v-if="profile.messenger" class="profile-public-chip">
            <span class="profile-public-chip-label">Messenger</span>
            {{ profile.messenger }}
          </span>
        </div>

        <div v-if="!hideActions" class="mt-6 flex flex-wrap justify-center gap-3 sm:justify-start">
          <button
            v-if="!isAuthenticated"
            class="profile-public-button rounded-full border px-5 py-2.5 text-sm font-semibold transition hover:brightness-110"
            :style="buttonStyle"
            type="button"
            @click="emit('openAuth')"
          >
            Đăng nhập / Đăng ký
          </button>
          <a
            href="#booking-section"
            class="profile-public-ghost rounded-full border px-5 py-2.5 text-sm font-medium transition hover:bg-black/5"
          >
            Đặt lịch ngay
          </a>
        </div>
      </div>
    </div>
  </section>
</template>
