<script setup lang="ts">
import type { GalleryItem } from '@/types/profile'

defineProps<{
  items: GalleryItem[]
  layout?: string
}>()
</script>

<template>
  <section class="profile-section">
    <p class="profile-section__label">Thư viện ảnh</p>
    <div
      class="profile-gallery"
      :class="layout === 'carousel' ? 'profile-gallery--carousel' : 'profile-gallery--grid'"
    >
      <figure
        v-for="(item, index) in items"
        :key="`${item.url}-${index}`"
        class="profile-gallery__item"
      >
        <img :src="item.url" :alt="item.alt ?? 'Ảnh thư viện'" class="profile-gallery__image" />
        <figcaption v-if="item.caption" class="profile-gallery__caption">{{ item.caption }}</figcaption>
      </figure>
    </div>
  </section>
</template>
