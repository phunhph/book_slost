<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()
const { items } = storeToRefs(toast)
</script>

<template>
  <Teleport to="body">
    <div class="toast-viewport" aria-live="polite" aria-relevant="additions">
      <TransitionGroup name="toast">
        <div
          v-for="item in items"
          :key="item.id"
          class="toast-item"
          :class="`toast-item--${item.type}`"
          role="alert"
        >
          <p class="toast-item__message">{{ item.message }}</p>
          <button
            type="button"
            class="toast-item__close"
            aria-label="Dismiss notification"
            @click="toast.dismiss(item.id)"
          >
            ×
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
