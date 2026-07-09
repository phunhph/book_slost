<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import ColorField from './ColorField.vue'
import {
  buildLinearGradient,
  parseLinearGradient,
  suggestPrimaryForGradient,
  suggestTextColorForGradient,
} from '../../lib/colorUtils'

const props = defineProps<{
  bgType: string | null | undefined
  modelValue: string | null | undefined
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  applyTheme: [theme: { textColor: string; primaryColor: string }]
}>()

const mode = ref<'palette' | 'code'>('palette')
const codeInput = ref(props.modelValue ?? '')

const gradient = reactive({
  angle: 135,
  start: '#FDF2F8',
  end: '#E0F2FE',
})

function syncGradientFromValue(value: string | null | undefined) {
  const parsed = parseLinearGradient(value)
  if (!parsed) return
  gradient.angle = parsed.angle
  gradient.start = parsed.start
  gradient.end = parsed.end
}

watch(
  () => props.modelValue,
  (value) => {
    codeInput.value = value ?? ''
    if (props.bgType === 'gradient') {
      syncGradientFromValue(value)
    }
  },
  { immediate: true },
)

watch(
  () => props.bgType,
  (type) => {
    if (type === 'gradient') {
      syncGradientFromValue(props.modelValue)
      if (!props.modelValue) {
        applyGradient()
      }
    }
  },
)

const gradientPreviewStyle = computed(() => ({
  background: buildLinearGradient(gradient.angle, gradient.start, gradient.end),
}))

function emitTheme(theme: { textColor: string; primaryColor: string }) {
  emit('applyTheme', theme)
}

function applyGradient() {
  const value = buildLinearGradient(gradient.angle, gradient.start, gradient.end)
  emit('update:modelValue', value)
  codeInput.value = value
  emitTheme({
    textColor: suggestTextColorForGradient(gradient.start, gradient.end),
    primaryColor: suggestPrimaryForGradient(gradient.start, gradient.end),
  })
}

function applyCode() {
  emit('update:modelValue', codeInput.value.trim())
}
</script>

<template>
  <div class="md:col-span-2">
    <div v-if="bgType === 'color'">
      <ColorField
        :model-value="modelValue"
        label="Màu nền"
        @update:model-value="emit('update:modelValue', $event)"
      />
    </div>

    <div v-else-if="bgType === 'gradient'" class="space-y-3">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <label class="text-sm text-slate-300">Nền gradient</label>
        <div class="color-field__tabs">
          <button
            class="color-field__tab"
            :class="{ 'color-field__tab--active': mode === 'palette' }"
            type="button"
            @click="mode = 'palette'"
          >
            Bảng màu
          </button>
          <button
            class="color-field__tab"
            :class="{ 'color-field__tab--active': mode === 'code' }"
            type="button"
            @click="mode = 'code'"
          >
            Mã CSS
          </button>
        </div>
      </div>

      <div v-if="mode === 'palette'" class="rounded-2xl border border-white/8 bg-white/3 p-4">
        <div class="mb-4 h-14 rounded-xl border border-white/10" :style="gradientPreviewStyle" />

        <div class="grid gap-3 lg:grid-cols-2">
          <ColorField v-model="gradient.start" compact label="Màu bắt đầu" @update:model-value="applyGradient" />
          <ColorField v-model="gradient.end" compact label="Màu kết thúc" @update:model-value="applyGradient" />
        </div>

        <label class="mt-4 block text-sm text-slate-300">
          Góc gradient: {{ gradient.angle }}°
          <input
            v-model.number="gradient.angle"
            class="mt-2 w-full accent-fuchsia-500"
            max="360"
            min="0"
            type="range"
            @input="applyGradient"
          />
        </label>


      </div>

      <div v-else class="rounded-2xl border border-white/8 bg-white/3 p-4">
        <textarea
          v-model="codeInput"
          class="field min-h-28 font-mono text-sm"
          placeholder="linear-gradient(135deg, #fdf2f8 0%, #e0f2fe 100%)"
        />
        <button class="btn-secondary mt-3" type="button" @click="applyCode">Áp dụng mã CSS</button>
      </div>
    </div>

    <div v-else>
      <label class="mb-2 block text-sm text-slate-300">Ảnh nền (URL)</label>
      <input
        :value="modelValue ?? ''"
        class="field min-w-0"
        placeholder="https://images.unsplash.com/..."
        type="url"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      />
      <p class="mt-2 text-xs text-slate-400">Dán link ảnh công khai để làm nền profile.</p>
    </div>
  </div>
</template>

<style scoped>
.color-field__tabs {
  display: inline-flex;
  gap: 0.25rem;
  padding: 0.2rem;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
}

.color-field__tab {
  border: none;
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #cbd5e1;
  background: transparent;
  cursor: pointer;
}

.color-field__tab--active {
  color: #fff;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.55), rgba(217, 70, 239, 0.55));
}

.gradient-preset__bar {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.gradient-preset__sample {
  font-size: 0.95rem;
  font-weight: 700;
  text-shadow: 0 1px 8px rgba(0, 0, 0, 0.18);
}
</style>
