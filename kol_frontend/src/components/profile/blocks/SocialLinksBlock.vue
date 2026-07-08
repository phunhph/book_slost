<script setup lang="ts">
import SocialPlatformIcon from '@/components/profile/SocialPlatformIcon.vue'
import { SOCIAL_PLATFORM_LABELS } from '@/lib/profileBlocks'
import type { SocialLinkItem } from '@/types/profile'

defineProps<{
  items: SocialLinkItem[]
}>()

function label(item: SocialLinkItem) {
  return item.label?.trim() || SOCIAL_PLATFORM_LABELS[item.platform] || item.platform
}
</script>

<template>
  <section class="profile-section">
    <p class="profile-section__label">Kết nối</p>
    <div class="flex flex-wrap gap-3">
      <a
        v-for="(item, index) in items"
        :key="`${item.platform}-${index}`"
        :href="item.url"
        :title="label(item)"
        :aria-label="label(item)"
        target="_blank"
        rel="noreferrer"
        class="profile-social-link"
      >
        <SocialPlatformIcon :platform="item.platform" />
      </a>
    </div>
  </section>
</template>
