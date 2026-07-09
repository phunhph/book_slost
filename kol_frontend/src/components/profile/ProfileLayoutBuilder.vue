<script setup lang="ts">
import { computed } from 'vue'

import {
  BLOCK_LIBRARY,
  SOCIAL_PLATFORM_LABELS,
  createBlock,
  migrateLayoutToV2,
  normalizeLayoutV2,
} from '@/lib/profileBlocks'
import RichTextEditor from '@/components/ui/RichTextEditor.vue'
import type { BlockType, GalleryItem, ProfileBlock, ProfileLayoutV2, QrCodeItem, SocialLinkItem } from '@/types/profile'

const props = withDefaults(
  defineProps<{
    mode?: 'all' | 'content'
  }>(),
  { mode: 'all' },
)

const layout = defineModel<ProfileLayoutV2>({ required: true })

const sortedBlocks = computed(() => {
  const blocks = migrateLayoutToV2(layout.value).blocks
  if (props.mode === 'content') {
    return blocks.filter((block) => ['about', 'gallery', 'qr_codes', 'booking'].includes(block.type))
  }
  return blocks
})

const availableBlocks = computed(() => {
  const existing = new Set(sortedBlocks.value.map((block) => block.type))
  const library =
    props.mode === 'content'
      ? BLOCK_LIBRARY.filter((item) => ['about', 'gallery', 'qr_codes'].includes(item.type))
      : BLOCK_LIBRARY
  return library.filter((item) => !existing.has(item.type))
})

const blockLabels: Record<BlockType, string> = {
  hero: 'Hero đầu trang',
  social_links: 'Mạng xã hội',
  gallery: 'Thư viện ảnh',
  qr_codes: 'Mã QR',
  about: 'Giới thiệu',
  booking: 'Form đặt lịch',
  contact: 'Liên hệ',
}

function commitBlocks(blocks: ProfileBlock[]) {
  layout.value = normalizeLayoutV2({ version: 2, blocks })
}

function updateBlock(blockId: string, updater: (block: ProfileBlock) => ProfileBlock) {
  commitBlocks(sortedBlocks.value.map((block) => (block.id === blockId ? updater(block) : block)))
}

function toggleBlock(blockId: string, active: boolean) {
  updateBlock(blockId, (block) => ({ ...block, active }))
}

function moveBlock(blockId: string, direction: -1 | 1) {
  const blocks = [...sortedBlocks.value]
  const index = blocks.findIndex((block) => block.id === blockId)
  const target = index + direction
  if (index < 0 || target < 0 || target >= blocks.length) return
  const [item] = blocks.splice(index, 1)
  blocks.splice(target, 0, item)
  commitBlocks(blocks.map((block, order) => ({ ...block, order })))
}

function addBlock(type: BlockType) {
  commitBlocks([...sortedBlocks.value, createBlock(type, sortedBlocks.value.length)])
}

function removeBlock(blockId: string) {
  const block = sortedBlocks.value.find((item) => item.id === blockId)
  if (!block || block.type === 'hero' || block.type === 'booking') return
  commitBlocks(sortedBlocks.value.filter((item) => item.id !== blockId))
}

function socialItems(block: ProfileBlock): SocialLinkItem[] {
  return (block.data.items as SocialLinkItem[] | undefined) ?? []
}

function galleryItems(block: ProfileBlock): GalleryItem[] {
  return (block.data.items as GalleryItem[] | undefined) ?? []
}

function qrItems(block: ProfileBlock): QrCodeItem[] {
  return (block.data.items as QrCodeItem[] | undefined) ?? []
}

function setSocialItems(blockId: string, items: SocialLinkItem[]) {
  updateBlock(blockId, (block) => ({ ...block, data: { ...block.data, items } }))
}

function setGalleryItems(blockId: string, items: GalleryItem[]) {
  updateBlock(blockId, (block) => ({ ...block, data: { ...block.data, items } }))
}

function setQrItems(blockId: string, items: QrCodeItem[]) {
  updateBlock(blockId, (block) => ({ ...block, data: { ...block.data, items } }))
}
</script>

<template>
  <div class="space-y-4">
    <p v-if="mode === 'content'" class="rounded-xl border border-white/8 bg-white/3 px-4 py-3 text-sm text-slate-400">
      Hero, kết nối và liên hệ được quản lý ở tab <strong class="text-slate-200">Kết nối</strong>. Ở đây chỉ chỉnh nội dung chi tiết và form đặt lịch.
    </p>
    <div
      v-for="(block, index) in sortedBlocks"
      :key="block.id"
      class="rounded-2xl border border-white/8 bg-white/4 p-4 sm:p-5"
    >
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p class="font-medium text-white">{{ blockLabels[block.type] }}</p>
          <p class="mt-1 text-xs text-slate-400">{{ block.type }}</p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <label class="flex items-center gap-2 text-sm text-slate-300">
            <input
              :checked="block.active"
              class="size-4 accent-fuchsia-500"
              type="checkbox"
              @change="toggleBlock(block.id, ($event.target as HTMLInputElement).checked)"
            />
            Hiện
          </label>
          <button class="btn-secondary px-3 py-2 text-xs" type="button" :disabled="index === 0" @click="moveBlock(block.id, -1)">
            Lên
          </button>
          <button
            class="btn-secondary px-3 py-2 text-xs"
            type="button"
            :disabled="index === sortedBlocks.length - 1"
            @click="moveBlock(block.id, 1)"
          >
            Xuống
          </button>
          <button
            v-if="block.type !== 'hero' && block.type !== 'booking'"
            class="btn-secondary px-3 py-2 text-xs text-rose-200"
            type="button"
            @click="removeBlock(block.id)"
          >
            Xóa
          </button>
        </div>
      </div>

      <div v-if="block.type === 'hero'" class="mt-4 text-sm text-slate-400">
        Dùng tên hiển thị, username, avatar và bio từ phần cài đặt hồ sơ phía trên.
      </div>

      <div v-else-if="block.type === 'about'" class="mt-4">
        <label class="mb-2 block text-sm text-slate-300">Nội dung giới thiệu</label>
        <RichTextEditor
          :model-value="String(block.data.content ?? '')"
          placeholder="Giới thiệu chi tiết, thành tích, gói dịch vụ..."
          @update:model-value="updateBlock(block.id, (item) => ({ ...item, data: { ...item.data, content: $event } }))"
        />
      </div>

      <div v-else-if="block.type === 'contact'" class="mt-4 grid gap-3 sm:grid-cols-3">
        <div>
          <label class="mb-2 block text-sm text-slate-300">Điện thoại</label>
          <input
            :value="String(block.data.phone ?? '')"
            class="field"
            type="text"
            @input="updateBlock(block.id, (item) => ({ ...item, data: { ...item.data, phone: ($event.target as HTMLInputElement).value } }))"
          />
        </div>
        <div>
          <label class="mb-2 block text-sm text-slate-300">Zalo</label>
          <input
            :value="String(block.data.zalo ?? '')"
            class="field"
            type="text"
            @input="updateBlock(block.id, (item) => ({ ...item, data: { ...item.data, zalo: ($event.target as HTMLInputElement).value } }))"
          />
        </div>
        <div>
          <label class="mb-2 block text-sm text-slate-300">Messenger</label>
          <input
            :value="String(block.data.messenger ?? '')"
            class="field"
            type="text"
            @input="updateBlock(block.id, (item) => ({ ...item, data: { ...item.data, messenger: ($event.target as HTMLInputElement).value } }))"
          />
        </div>
      </div>

      <div v-else-if="block.type === 'booking'" class="mt-4 grid gap-3 sm:grid-cols-2">
        <div>
          <label class="mb-2 block text-sm text-slate-300">Tiêu đề</label>
          <input
            :value="String(block.data.title ?? '')"
            class="field"
            type="text"
            @input="updateBlock(block.id, (item) => ({ ...item, data: { ...item.data, title: ($event.target as HTMLInputElement).value } }))"
          />
        </div>
        <div>
          <label class="mb-2 block text-sm text-slate-300">Phụ đề</label>
          <input
            :value="String(block.data.subtitle ?? '')"
            class="field"
            type="text"
            @input="updateBlock(block.id, (item) => ({ ...item, data: { ...item.data, subtitle: ($event.target as HTMLInputElement).value } }))"
          />
        </div>
      </div>

      <div v-else-if="block.type === 'social_links'" class="mt-4 space-y-4">
        <div
          v-for="(item, itemIndex) in socialItems(block)"
          :key="itemIndex"
          class="block-editor-item"
        >
          <div class="grid gap-3 md:grid-cols-2">
            <div class="min-w-0">
              <label class="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-400">Nền tảng</label>
              <select
                :value="item.platform"
                class="field min-w-0"
                @change="setSocialItems(block.id, socialItems(block).map((row, idx) => idx === itemIndex ? { ...row, platform: ($event.target as HTMLSelectElement).value } : row))"
              >
                <option v-for="(label, platform) in SOCIAL_PLATFORM_LABELS" :key="platform" :value="platform">{{ label }}</option>
              </select>
            </div>
            <div class="min-w-0">
              <label class="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-400">Nhãn</label>
              <input
                :value="item.label ?? ''"
                class="field min-w-0"
                placeholder="VD: Instagram chính"
                type="text"
                @input="setSocialItems(block.id, socialItems(block).map((row, idx) => idx === itemIndex ? { ...row, label: ($event.target as HTMLInputElement).value } : row))"
              />
            </div>
          </div>
          <div class="mt-3 min-w-0">
            <label class="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-400">URL</label>
            <input
              :value="item.url"
              class="field min-w-0"
              placeholder="https://instagram.com/username"
              type="url"
              @input="setSocialItems(block.id, socialItems(block).map((row, idx) => idx === itemIndex ? { ...row, url: ($event.target as HTMLInputElement).value } : row))"
            />
          </div>
          <div class="mt-3 flex justify-end">
            <button
              class="btn-secondary px-4 py-2 text-xs text-rose-200"
              type="button"
              @click="setSocialItems(block.id, socialItems(block).filter((_, idx) => idx !== itemIndex))"
            >
              Xóa link
            </button>
          </div>
        </div>
        <button
          class="btn-secondary w-full text-sm sm:w-auto"
          type="button"
          @click="setSocialItems(block.id, [...socialItems(block), { platform: 'website', label: '', url: '' }])"
        >
          + Thêm liên kết mạng xã hội
        </button>
      </div>

      <div v-else-if="block.type === 'gallery'" class="mt-4 space-y-4">
        <div>
          <label class="mb-2 block text-sm text-slate-300">Bố cục</label>
          <select
            :value="String(block.data.layout ?? 'grid')"
            class="field max-w-xs"
            @change="updateBlock(block.id, (item) => ({ ...item, data: { ...item.data, layout: ($event.target as HTMLSelectElement).value } }))"
          >
            <option value="grid">Lưới</option>
            <option value="carousel">Carousel</option>
          </select>
        </div>
        <div
          v-for="(item, itemIndex) in galleryItems(block)"
          :key="itemIndex"
          class="block-editor-item"
        >
          <div class="min-w-0">
            <label class="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-400">URL ảnh</label>
            <input
              :value="item.url"
              class="field min-w-0"
              placeholder="https://images.unsplash.com/..."
              type="url"
              @input="setGalleryItems(block.id, galleryItems(block).map((row, idx) => idx === itemIndex ? { ...row, url: ($event.target as HTMLInputElement).value } : row))"
            />
          </div>
          <div class="mt-3 grid gap-3 md:grid-cols-2">
            <div class="min-w-0">
              <label class="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-400">Mô tả ảnh</label>
              <input
                :value="item.alt ?? ''"
                class="field min-w-0"
                placeholder="Mô tả ảnh"
                type="text"
                @input="setGalleryItems(block.id, galleryItems(block).map((row, idx) => idx === itemIndex ? { ...row, alt: ($event.target as HTMLInputElement).value } : row))"
              />
            </div>
            <div class="min-w-0">
              <label class="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-400">Chú thích</label>
              <input
                :value="item.caption ?? ''"
                class="field min-w-0"
                placeholder="Chú thích"
                type="text"
                @input="setGalleryItems(block.id, galleryItems(block).map((row, idx) => idx === itemIndex ? { ...row, caption: ($event.target as HTMLInputElement).value } : row))"
              />
            </div>
          </div>
          <div class="mt-3 flex justify-end">
            <button
              class="btn-secondary px-4 py-2 text-xs text-rose-200"
              type="button"
              @click="setGalleryItems(block.id, galleryItems(block).filter((_, idx) => idx !== itemIndex))"
            >
              Xóa ảnh
            </button>
          </div>
        </div>
        <button
          class="btn-secondary w-full text-sm sm:w-auto"
          type="button"
          @click="setGalleryItems(block.id, [...galleryItems(block), { url: '', alt: '', caption: '' }])"
        >
          + Thêm ảnh
        </button>
      </div>

      <div v-else-if="block.type === 'qr_codes'" class="mt-4 space-y-4">
        <div
          v-for="(item, itemIndex) in qrItems(block)"
          :key="itemIndex"
          class="block-editor-item"
        >
          <div class="grid gap-3 md:grid-cols-2">
            <div class="min-w-0">
              <label class="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-400">Nhãn</label>
              <input
                :value="item.label"
                class="field min-w-0"
                placeholder="Zalo QR"
                type="text"
                @input="setQrItems(block.id, qrItems(block).map((row, idx) => idx === itemIndex ? { ...row, label: ($event.target as HTMLInputElement).value } : row))"
              />
            </div>
            <div class="min-w-0">
              <label class="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-400">URL ảnh QR</label>
              <input
                :value="item.image_url"
                class="field min-w-0"
                placeholder="https://..."
                type="url"
                @input="setQrItems(block.id, qrItems(block).map((row, idx) => idx === itemIndex ? { ...row, image_url: ($event.target as HTMLInputElement).value } : row))"
              />
            </div>
          </div>
          <div class="mt-3 min-w-0">
            <label class="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-400">URL đích (tuỳ chọn)</label>
            <input
              :value="item.target_url ?? ''"
              class="field min-w-0"
              placeholder="https://zalo.me/..."
              type="url"
              @input="setQrItems(block.id, qrItems(block).map((row, idx) => idx === itemIndex ? { ...row, target_url: ($event.target as HTMLInputElement).value } : row))"
            />
          </div>
          <div class="mt-3 flex justify-end">
            <button
              class="btn-secondary px-4 py-2 text-xs text-rose-200"
              type="button"
              @click="setQrItems(block.id, qrItems(block).filter((_, idx) => idx !== itemIndex))"
            >
              Xóa QR
            </button>
          </div>
        </div>
        <button
          class="btn-secondary w-full text-sm sm:w-auto"
          type="button"
          @click="setQrItems(block.id, [...qrItems(block), { label: 'QR', image_url: '', target_url: '' }])"
        >
          + Thêm QR code
        </button>
      </div>
    </div>

    <div v-if="availableBlocks.length" class="rounded-2xl border border-dashed border-white/12 p-4">
      <p class="text-sm font-medium text-white">Thêm block</p>
      <div class="mt-3 flex flex-wrap gap-2">
        <button
          v-for="item in availableBlocks"
          :key="item.type"
          class="btn-secondary text-sm"
          type="button"
          @click="addBlock(item.type)"
        >
          + {{ item.label }}
        </button>
      </div>
    </div>
  </div>
</template>
