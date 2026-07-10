<script setup lang="ts">
import SocialPlatformIcon from '@/components/profile/SocialPlatformIcon.vue'
import { SOCIAL_PLATFORM_LABELS } from '@/lib/profileBlocks'
import type { SocialLinkItem } from '@/types/profile'

const props = defineProps<{
  socialItems: SocialLinkItem[]
  phone: string
  zalo: string
  messenger: string
  contactLinks?: Array<{ platform: string; value: string; label?: string }>
}>()

function socialLabel(item: SocialLinkItem) {
  return item.label?.trim() || SOCIAL_PLATFORM_LABELS[item.platform] || item.platform
}

const hasSocial = () => props.socialItems.some((item) => item.url?.trim())

const hasContact = () => {
  if (props.contactLinks && props.contactLinks.length > 0) {
    return true
  }
  return Boolean(props.phone || props.zalo || props.messenger)
}

function formatPlatformLabel(plat: string) {
  return (
    {
      phone: 'Điện thoại',
      zalo: 'Zalo',
      messenger: 'Messenger',
      telegram: 'Telegram',
      viber: 'Viber',
      instagram: 'Instagram',
      tiktok: 'TikTok',
      youtube: 'YouTube',
      shopee: 'Shopee',
      website: 'Website',
    }[plat] || plat
  )
}

function formatDisplayValue(val: string) {
  if (!val) return ''
  try {
    const url = new URL(val)
    return url.hostname + (url.pathname !== '/' ? url.pathname : '')
  } catch {
    return val
  }
}
</script>

<template>
  <section v-if="hasSocial() || hasContact()" class="profile-connect-zone">
    <div class="profile-connect-zone__inner">
      <p class="profile-connect-zone__title">Kết nối</p>

      <div v-if="hasSocial()" class="profile-connect-zone__social">
        <a
          v-for="(item, index) in socialItems.filter((row) => row.url?.trim())"
          :key="`${item.platform}-${index}`"
          :href="item.url"
          :title="socialLabel(item)"
          :aria-label="socialLabel(item)"
          target="_blank"
          rel="noreferrer"
          class="profile-connect-zone__social-link"
        >
          <SocialPlatformIcon :platform="item.platform" />
          <span>{{ socialLabel(item) }}</span>
        </a>
      </div>

      <div v-if="hasContact()" class="profile-connect-zone__contacts">
        <template v-if="contactLinks && contactLinks.length > 0">
          <template v-for="(link, index) in contactLinks" :key="index">
            <a
              v-if="link.platform === 'phone' || link.value.startsWith('tel:')"
              class="profile-connect-zone__chip hover:bg-white/10"
              :href="link.value.startsWith('tel:') ? link.value : `tel:${link.value}`"
            >
              <span class="profile-connect-zone__chip-label">{{ link.label || 'Điện thoại' }}</span>
              <span>{{ link.value.replace('tel:', '') }}</span>
            </a>
            <a
              v-else-if="link.value.startsWith('http')"
              class="profile-connect-zone__chip hover:bg-white/10"
              :href="link.value"
              target="_blank"
              rel="noopener noreferrer"
            >
              <span class="profile-connect-zone__chip-label">{{ link.label || formatPlatformLabel(link.platform) }}</span>
              <span>{{ formatDisplayValue(link.value) }}</span>
            </a>
            <span v-else class="profile-connect-zone__chip">
              <span class="profile-connect-zone__chip-label">{{ link.label || formatPlatformLabel(link.platform) }}</span>
              <span>{{ link.value }}</span>
            </span>
          </template>
        </template>

        <template v-else>
          <a v-if="phone" class="profile-connect-zone__chip hover:bg-white/10" :href="`tel:${phone}`">
            <span class="profile-connect-zone__chip-label">Điện thoại</span>
            <span>{{ phone }}</span>
          </a>
          <span v-if="zalo" class="profile-connect-zone__chip">
            <span class="profile-connect-zone__chip-label">Zalo</span>
            <span>{{ zalo }}</span>
          </span>
          <span v-if="messenger" class="profile-connect-zone__chip">
            <span class="profile-connect-zone__chip-label">Messenger</span>
            <span>{{ messenger }}</span>
          </span>
        </template>
      </div>
    </div>
  </section>
</template>
