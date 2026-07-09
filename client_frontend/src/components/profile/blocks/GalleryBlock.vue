<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { GalleryItem } from '@/types/profile'

const props = defineProps<{
  items: GalleryItem[]
  layout?: string
}>()

const currentIndex = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

function next() {
  if (props.items.length <= 1) return
  currentIndex.value = (currentIndex.value + 1) % props.items.length
}

function prev() {
  if (props.items.length <= 1) return
  currentIndex.value = (currentIndex.value - 1 + props.items.length) % props.items.length
}

function setIndex(index: number) {
  currentIndex.value = index
}

function startTimer() {
  if (props.items.length > 1 && !timer) {
    timer = setInterval(next, 4000)
  }
}

function stopTimer() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

onMounted(() => {
  startTimer()
})

onUnmounted(() => {
  stopTimer()
})
</script>

<template>
  <section class="profile-section">
    <p class="profile-section__label">Thư viện ảnh</p>
    
    <div 
      v-if="items.length > 0" 
      @mouseenter="stopTimer" 
      @mouseleave="startTimer"
      class="relative group mt-4 overflow-hidden rounded-2xl border border-white/10 bg-white/5 shadow-xl max-w-lg mx-auto"
    >
      <!-- Slideshow Container -->
      <div class="relative w-full aspect-[4/3] overflow-hidden flex items-center justify-center">
        <Transition name="fade" mode="out-in">
          <div :key="currentIndex" class="w-full h-full relative flex flex-col justify-between">
            <img 
              :src="items[currentIndex].url" 
              :alt="items[currentIndex].alt ?? 'Ảnh thư viện'" 
              class="w-full h-full object-cover" 
            />
            <div 
              v-if="items[currentIndex].caption" 
              class="absolute bottom-0 inset-x-0 bg-gradient-to-t from-slate-950/80 to-transparent p-4 pt-12 text-slate-100 text-sm font-medium"
            >
              {{ items[currentIndex].caption }}
            </div>
          </div>
        </Transition>
      </div>

      <!-- Navigation Arrows (Faded out by default, reveal on container hover) -->
      <template v-if="items.length > 1">
        <button 
          type="button"
          @click="prev"
          class="absolute left-3 top-1/2 -translate-y-1/2 flex items-center justify-center h-9 w-9 rounded-full bg-slate-950/30 hover:bg-slate-950/70 border border-white/8 text-white/70 hover:text-white transition-all duration-300 z-10 opacity-0 group-hover:opacity-100 cursor-pointer pointer-events-auto"
          aria-label="Previous Slide"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
          </svg>
        </button>
        <button 
          type="button"
          @click="next"
          class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center justify-center h-9 w-9 rounded-full bg-slate-950/30 hover:bg-slate-950/70 border border-white/8 text-white/70 hover:text-white transition-all duration-300 z-10 opacity-0 group-hover:opacity-100 cursor-pointer pointer-events-auto"
          aria-label="Next Slide"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
          </svg>
        </button>
      </template>

      <!-- Indicator Dots -->
      <div v-if="items.length > 1" class="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5 z-10">
        <button 
          v-for="(_, index) in items" 
          :key="index"
          type="button"
          @click="setIndex(index)"
          class="h-1.5 rounded-full transition-all duration-300"
          :class="currentIndex === index ? 'w-5 bg-white' : 'w-1.5 bg-white/40 hover:bg-white/60'"
          :aria-label="`Go to slide ${index + 1}`"
        />
      </div>
    </div>
    
    <div v-else class="text-sm text-slate-400 py-6 text-center border border-dashed border-white/10 rounded-2xl">
      Chưa có ảnh trong thư viện.
    </div>
  </section>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
