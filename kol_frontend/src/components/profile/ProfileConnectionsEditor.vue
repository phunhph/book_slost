<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { ensureLayoutBlocks, normalizeLayoutV2 } from '@/lib/profileBlocks'
import type { ProfileLayoutV2, SocialLinkItem } from '@/types/profile'
import { getPublicPlatforms } from '../../services/api'

const layout = defineModel<ProfileLayoutV2>({ required: true })

const phone = defineModel<string | null>('phone', { default: null })
const zalo = defineModel<string | null>('zalo', { default: null })
const messenger = defineModel<string | null>('messenger', { default: null })
const contactLinks = defineModel<Array<{ platform: string; value: string; label?: string }> | null | undefined>('contactLinks', { default: () => [] })

const safeContactLinks = computed({
  get: () => contactLinks.value || [],
  set: (val) => { contactLinks.value = val }
})

const contactOptions = ref([
  { value: 'phone', label: 'Điện thoại' },
  { value: 'zalo', label: 'Zalo' },
  { value: 'messenger', label: 'Facebook Messenger' },
  { value: 'telegram', label: 'Telegram' },
  { value: 'viber', label: 'Viber' },
])

const socialOptions = ref([
  { value: 'instagram', label: 'Instagram' },
  { value: 'tiktok', label: 'TikTok' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'youtube', label: 'YouTube' },
  { value: 'twitter', label: 'X / Twitter' },
  { value: 'shopee', label: 'Shopee' },
  { value: 'website', label: 'Website' },
])

onMounted(async () => {
  try {
    const list = await getPublicPlatforms()
    const active = list.filter((p) => p.is_active)
    
    contactOptions.value = active
      .filter((p) => p.category === 'contact')
      .map((p) => ({ value: p.key, label: p.label }))
      
    socialOptions.value = active
      .filter((p) => p.category === 'social')
      .map((p) => ({ value: p.key, label: p.label }))
  } catch (error) {
    console.error('Failed to load dynamic platforms on profile connections config:', error)
  }
})

const normalized = computed(() => ensureLayoutBlocks(layout.value))

const socialBlock = computed(() => normalized.value.blocks.find((block) => block.type === 'social_links')!)

const socialItems = computed({
  get: () => (socialBlock.value.data.items as SocialLinkItem[] | undefined) ?? [],
  set: (items: SocialLinkItem[]) => {
    layout.value = normalizeLayoutV2({
      version: 2,
      blocks: normalized.value.blocks.map((block) =>
        block.type === 'social_links' ? { ...block, active: true, data: { ...block.data, items } } : block,
      ),
    })
  },
})

function commitContactFields() {
  // Sync to legacy flat fields for compatibility
  let phoneVal: string | null = null
  let zaloVal: string | null = null
  let messengerVal: string | null = null
  
  for (const link of safeContactLinks.value) {
    if (link.platform === 'phone' && !phoneVal) {
      phoneVal = link.value
    } else if (link.platform === 'zalo' && !zaloVal) {
      zaloVal = link.value
    } else if (link.platform === 'messenger' && !messengerVal) {
      messengerVal = link.value
    }
  }
  
  phone.value = phoneVal
  zalo.value = zaloVal
  messenger.value = messengerVal

  layout.value = normalizeLayoutV2({
    version: 2,
    blocks: normalized.value.blocks.map((block) => {
      if (block.type !== 'contact') return block
      const hasValue = safeContactLinks.value.some(l => l.value.trim() !== '')
      return {
        ...block,
        active: hasValue,
        data: { phone: phone.value, zalo: zalo.value, messenger: messenger.value },
      }
    }),
  })
}

function addContactLink() {
  const defaultPlat = contactOptions.value[0]?.value || 'phone'
  safeContactLinks.value.push({ platform: defaultPlat, value: '', label: '' })
  commitContactFields()
}

function removeContactLink(index: number) {
  safeContactLinks.value.splice(index, 1)
  commitContactFields()
}

function addSocialLink() {
  const defaultPlat = socialOptions.value[0]?.value || 'instagram'
  socialItems.value = [...socialItems.value, { platform: defaultPlat, label: '', url: '' }]
}

function updateSocial(index: number, patch: Partial<SocialLinkItem>) {
  socialItems.value = socialItems.value.map((row, idx) => (idx === index ? { ...row, ...patch } : row))
}

function removeSocial(index: number) {
  socialItems.value = socialItems.value.filter((_, idx) => idx !== index)
}

layout.value = ensureLayoutBlocks(layout.value)
commitContactFields()
</script>

<template>
  <div class="space-y-5">
    <div class="profile-form-section">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p class="profile-form-section__title !mb-1">Liên hệ trực tiếp</p>
          <p class="text-sm text-slate-400">Hiển thị ngay dưới phần hero trên trang công khai.</p>
        </div>
        <button class="btn-secondary text-sm !h-8 !py-0 px-3 flex items-center justify-center cursor-pointer" type="button" @click="addContactLink">+ Thêm liên hệ</button>
      </div>

      <div
        v-if="!safeContactLinks.length"
        class="mt-4 rounded-xl border border-dashed border-white/10 px-4 py-8 text-center text-sm text-slate-400"
      >
        Chưa có kênh liên hệ trực tiếp nào. Thêm số điện thoại hoặc mạng xã hội.
      </div>

      <div v-for="(item, index) in safeContactLinks" :key="index" class="block-editor-item mt-4">
        <div class="grid gap-3 md:grid-cols-3">
          <div>
            <label class="mb-2 block text-xs uppercase tracking-wide text-slate-400">Nền tảng</label>
            <select
              v-model="item.platform"
              class="field"
              @change="commitContactFields"
            >
              <option v-for="opt in contactOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="mb-2 block text-xs uppercase tracking-wide text-slate-400">Giá trị / Liên kết</label>
            <input
              v-model="item.value"
              class="field"
              placeholder="SĐT hoặc Link liên kết"
              type="text"
              @input="commitContactFields"
            />
          </div>
          <div>
            <label class="mb-2 block text-xs uppercase tracking-wide text-slate-400">Nhãn hiển thị</label>
            <input
              v-model="item.label"
              class="field"
              placeholder="VD: Hotline, Zalo cá nhân"
              type="text"
              @input="commitContactFields"
            />
          </div>
        </div>
        <div class="mt-3 flex justify-end">
          <button class="btn-secondary px-3 py-2 text-xs text-rose-200 cursor-pointer" type="button" @click="removeContactLink(index)">
            Xóa
          </button>
        </div>
      </div>
    </div>

    <div class="profile-form-section">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p class="profile-form-section__title !mb-1">Mạng xã hội & liên kết</p>
          <p class="text-sm text-slate-400">Instagram, TikTok, website… — cùng khu vực kết nối phía trên trang.</p>
        </div>
        <button class="btn-secondary text-sm !h-8 !py-0 px-3 flex items-center justify-center cursor-pointer" type="button" @click="addSocialLink">+ Thêm link</button>
      </div>

      <div
        v-if="!socialItems.length"
        class="mt-4 rounded-xl border border-dashed border-white/10 px-4 py-8 text-center text-sm text-slate-400"
      >
        Chưa có link nào. Thêm ít nhất một kênh để khách theo dõi bạn.
      </div>

      <div v-for="(item, index) in socialItems" :key="index" class="block-editor-item mt-4">
        <div class="grid gap-3 md:grid-cols-2">
          <div>
            <label class="mb-2 block text-xs uppercase tracking-wide text-slate-400">Nền tảng</label>
            <select
              :value="item.platform"
              class="field"
              @change="updateSocial(index, { platform: ($event.target as HTMLSelectElement).value })"
            >
              <option v-for="opt in socialOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="mb-2 block text-xs uppercase tracking-wide text-slate-400">Nhãn hiển thị</label>
            <input
              :value="item.label ?? ''"
              class="field"
              placeholder="VD: Instagram chính"
              type="text"
              @input="updateSocial(index, { label: ($event.target as HTMLInputElement).value })"
            />
          </div>
        </div>
        <div class="mt-3">
          <label class="mb-2 block text-xs uppercase tracking-wide text-slate-400">URL</label>
          <input
            :value="item.url"
            class="field"
            placeholder="https://..."
            type="url"
            @input="updateSocial(index, { url: ($event.target as HTMLInputElement).value })"
          />
        </div>
        <div class="mt-3 flex justify-end">
          <button class="btn-secondary px-3 py-2 text-xs text-rose-200 cursor-pointer" type="button" @click="removeSocial(index)">
            Xóa
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
