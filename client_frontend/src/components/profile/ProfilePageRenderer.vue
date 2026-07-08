<script setup lang="ts">
import { computed } from 'vue'

import AboutBlock from '@/components/profile/blocks/AboutBlock.vue'
import BookingBlock from '@/components/profile/blocks/BookingBlock.vue'
import ContactBlock from '@/components/profile/blocks/ContactBlock.vue'
import GalleryBlock from '@/components/profile/blocks/GalleryBlock.vue'
import HeroBlock from '@/components/profile/blocks/HeroBlock.vue'
import QrCodesBlock from '@/components/profile/blocks/QrCodesBlock.vue'
import SocialLinksBlock from '@/components/profile/blocks/SocialLinksBlock.vue'
import { getContactData, getVisibleBlocks } from '@/lib/profileBlocks'
import { buildProfileSurfaceStyle, profileAccentVars, withResolvedProfileTheme } from '@/lib/profileTheme'
import type { GalleryItem, QrCodeItem, SocialLinkItem, UserProfile } from '@/types/profile'

const props = withDefaults(
  defineProps<{
    profile: UserProfile
    preview?: boolean
  }>(),
  { preview: false },
)

const emit = defineEmits<{
  openAuth: []
}>()

const displayProfile = computed(() => withResolvedProfileTheme(props.profile))

const themedStyle = computed(() => ({
  ...buildProfileSurfaceStyle(displayProfile.value),
  ...profileAccentVars(displayProfile.value.primary_color),
}))

const blocks = computed(() => getVisibleBlocks(displayProfile.value))

const showBioInHero = computed(() => !blocks.value.some((block) => block.type === 'about'))
const showQuickContactInHero = computed(() => !blocks.value.some((block) => block.type === 'contact'))
</script>

<template>
  <div class="profile-page" :style="themedStyle">
    <div class="page-container profile-page__inner">
      <template v-for="block in blocks" :key="block.id">
        <HeroBlock
          v-if="block.type === 'hero'"
          :profile="displayProfile"
          :show-bio="showBioInHero"
          :show-quick-contact="showQuickContactInHero"
          :hide-actions="preview"
          @open-auth="emit('openAuth')"
        />

        <AboutBlock
          v-else-if="block.type === 'about'"
          :content="String(block.data.content ?? '')"
        />

        <ContactBlock
          v-else-if="block.type === 'contact'"
          v-bind="getContactData(block, displayProfile)"
        />

        <SocialLinksBlock
          v-else-if="block.type === 'social_links'"
          :items="(block.data.items as SocialLinkItem[]) ?? []"
        />

        <GalleryBlock
          v-else-if="block.type === 'gallery'"
          :items="(block.data.items as GalleryItem[]) ?? []"
          :layout="String(block.data.layout ?? 'grid')"
        />

        <QrCodesBlock
          v-else-if="block.type === 'qr_codes'"
          :items="(block.data.items as QrCodeItem[]) ?? []"
        />

        <BookingBlock
          v-else-if="block.type === 'booking'"
          :profile="displayProfile"
          :title="String(block.data.title ?? 'Gửi yêu cầu hợp tác')"
          :subtitle="String(block.data.subtitle ?? '')"
          @request-auth="emit('openAuth')"
        />
      </template>
    </div>
  </div>
</template>
