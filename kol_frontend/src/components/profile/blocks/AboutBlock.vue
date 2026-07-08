<script setup lang="ts">
import { computed } from 'vue'
import { isRichHtml, sanitizeRichHtml } from '@/lib/richText'

const props = defineProps<{
  content: string
}>()

const safeHtml = computed(() => sanitizeRichHtml(props.content))
const isPlainText = computed(() => !isRichHtml(props.content))
</script>

<template>
  <section class="profile-section">
    <p class="profile-section__label">About</p>
    <div
      v-if="isPlainText"
      class="profile-section__body profile-rich-text whitespace-pre-wrap"
    >
      {{ content }}
    </div>
    <div v-else class="profile-section__body profile-rich-text" v-html="safeHtml" />
  </section>
</template>
