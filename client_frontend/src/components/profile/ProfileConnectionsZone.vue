<script setup lang="ts">
import SocialPlatformIcon from '@/components/profile/SocialPlatformIcon.vue'
import { SOCIAL_PLATFORM_LABELS } from '@/lib/profileBlocks'
import type { SocialLinkItem } from '@/types/profile'

const props = defineProps<{
  socialItems: SocialLinkItem[]
  phone: string
  zalo: string
  messenger: string
}>()

function socialLabel(item: SocialLinkItem) {
  return item.label?.trim() || SOCIAL_PLATFORM_LABELS[item.platform] || item.platform
}

const hasSocial = () => props.socialItems.some((item) => item.url?.trim())
const hasContact = () => Boolean(props.phone || props.zalo || props.messenger)
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
        <a v-if="phone" class="profile-connect-zone__chip" :href="`tel:${phone}`">
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
      </div>
    </div>
  </section>
</template>
