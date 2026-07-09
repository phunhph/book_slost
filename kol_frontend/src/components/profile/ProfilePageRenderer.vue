<script setup lang="ts">
import { computed } from 'vue'

import AboutBlock from '@/components/profile/blocks/AboutBlock.vue'
import BookingPreviewBlock from '@/components/profile/blocks/BookingPreviewBlock.vue'
import GalleryBlock from '@/components/profile/blocks/GalleryBlock.vue'
import HeroBlock from '@/components/profile/blocks/HeroBlock.vue'
import QrCodesBlock from '@/components/profile/blocks/QrCodesBlock.vue'
import ProfileConnectionsZone from '@/components/profile/ProfileConnectionsZone.vue'
import { getContactData, getVisibleBlocks, isBlockVisible, parseLayout } from '@/lib/profileBlocks'
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

const layout = computed(() => parseLayout(displayProfile.value))
const visibleBlocks = computed(() => getVisibleBlocks(displayProfile.value))

const showBioInHero = computed(() => !visibleBlocks.value.some((block) => block.type === 'about'))

const socialBlock = computed(() => layout.value.blocks.find((block) => block.type === 'social_links'))
const contactBlock = computed(() => layout.value.blocks.find((block) => block.type === 'contact'))

const socialItems = computed(
  () => (socialBlock.value?.data.items as SocialLinkItem[] | undefined)?.filter((item) => item.url?.trim()) ?? [],
)

const contactData = computed(() => {
  if (contactBlock.value && isBlockVisible(contactBlock.value, displayProfile.value)) {
    return getContactData(contactBlock.value, displayProfile.value)
  }
  return {
    phone: displayProfile.value.phone || '',
    zalo: displayProfile.value.zalo || '',
    messenger: displayProfile.value.messenger || '',
  }
})

const contentBlocks = computed(() =>
  visibleBlocks.value.filter((block) => ['about', 'gallery', 'qr_codes'].includes(block.type)),
)

function getResolvedQrItems(blockItems: QrCodeItem[] | undefined) {
  const list = [...(blockItems ?? [])]
  if (displayProfile.value.bank_account_number && displayProfile.value.bank_name) {
    const bankId = encodeURIComponent(displayProfile.value.bank_name.trim())
    const accountNo = encodeURIComponent(displayProfile.value.bank_account_number.trim())
    const accountName = encodeURIComponent(displayProfile.value.bank_account_name || '')
    const exists = list.some(item => item.image_url?.includes(accountNo))
    if (!exists) {
      list.unshift({
        label: `QR Ngân hàng (${displayProfile.value.bank_name})`,
        image_url: `https://img.vietqr.io/image/${bankId}-${accountNo}-compact2.png?amount=0&addInfo=Chuyen%20khoan%20booking&accountName=${accountName}`,
        target_url: ''
      })
    }
  }
  return list
}

const bookingBlock = computed(() => visibleBlocks.value.find((block) => block.type === 'booking'))
</script>

<template>
  <div class="profile-page" :style="themedStyle">
    <div class="page-container profile-page__inner">
      <HeroBlock
        :profile="displayProfile"
        :show-bio="showBioInHero"
        :show-quick-contact="false"
        :hide-actions="preview"
        @open-auth="emit('openAuth')"
      />

      <ProfileConnectionsZone
        :social-items="socialItems"
        :phone="contactData.phone"
        :zalo="contactData.zalo"
        :messenger="contactData.messenger"
      />

      <div v-if="contentBlocks.length" class="profile-content-stack">
        <template v-for="block in contentBlocks" :key="block.id">
          <AboutBlock v-if="block.type === 'about'" :content="String(block.data.content ?? '')" />
          <GalleryBlock
            v-else-if="block.type === 'gallery'"
            :items="(block.data.items as GalleryItem[]) ?? []"
            :layout="String(block.data.layout ?? 'grid')"
          />
          <QrCodesBlock
            v-else-if="block.type === 'qr_codes'"
            :items="getResolvedQrItems(block.data.items as QrCodeItem[])"
          />
        </template>
      </div>

      <BookingPreviewBlock
        v-if="bookingBlock"
        :profile="displayProfile"
        :title="String(bookingBlock.data.title ?? 'Gửi yêu cầu hợp tác')"
        :subtitle="String(bookingBlock.data.subtitle ?? '')"
      />
    </div>
  </div>
</template>
