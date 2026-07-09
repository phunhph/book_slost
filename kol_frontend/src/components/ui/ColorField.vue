<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { COLOR_PRESETS, hexForColorInput, normalizeHex } from '../../lib/colorUtils'

const props = withDefaults(
  defineProps<{
    modelValue: string | null | undefined
    label: string
    compact?: boolean
  }>(),
  { compact: false },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const mode = ref<'palette' | 'code'>('palette')
const codeInput = ref(hexForColorInput(props.modelValue))

const pickerValue = computed({
  get() {
    return hexForColorInput(props.modelValue)
  },
  set(value: string) {
    const normalized = normalizeHex(value)
    if (normalized) {
      emit('update:modelValue', normalized)
      codeInput.value = normalized
    }
  },
})

const previewStyle = computed(() => ({
  background: hexForColorInput(props.modelValue),
}))

watch(
  () => props.modelValue,
  (value) => {
    codeInput.value = hexForColorInput(value)
  },
)

function selectPreset(color: string) {
  const normalized = normalizeHex(color)
  if (!normalized) return
  emit('update:modelValue', normalized)
  codeInput.value = normalized
}

function applyCode() {
  const normalized = normalizeHex(codeInput.value)
  if (!normalized) return
  emit('update:modelValue', normalized)
  codeInput.value = normalized
}
</script>

<template>
  <div class="color-field" :class="{ 'color-field--compact': compact }">
    <div class="mb-2 flex flex-wrap items-center justify-between gap-2">
      <label class="text-sm text-slate-300">{{ label }}</label>
      <div v-if="!compact" class="color-field__tabs">
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
          Mã màu
        </button>
      </div>
    </div>

    <div v-if="mode === 'palette' || compact" class="color-field__palette">
      <!-- Suggested color presets grid on top -->
      <div class="color-field__preset-grid">
        <button
          v-for="color in COLOR_PRESETS"
          :key="color"
          class="color-field__preset"
          :class="{ 'color-field__preset--active': hexForColorInput(modelValue) === normalizeHex(color) }"
          :style="{ background: color }"
          type="button"
          :title="color"
          @click="selectPreset(color)"
        />
      </div>

      <!-- Custom color picker at the bottom -->
      <div class="color-field__picker-row">
        <label class="color-field__picker-shell">
          <span class="color-field__swatch" :style="previewStyle" />
          <input v-model="pickerValue" class="color-field__picker" type="color" />
          <span class="text-sm text-slate-300">{{ compact ? hexForColorInput(modelValue) : 'Tự chọn màu khác' }}</span>
        </label>
        <code v-if="!compact" class="color-field__current">{{ hexForColorInput(modelValue) }}</code>
      </div>
    </div>

    <div v-else class="color-field__code">
      <div class="flex gap-2">
        <input
          v-model="codeInput"
          class="field font-mono uppercase"
          placeholder="#FF007F"
          type="text"
          @keydown.enter.prevent="applyCode"
        />
        <button class="btn-secondary shrink-0 px-4" type="button" @click="applyCode">Áp dụng</button>
      </div>
      <p class="mt-2 text-xs text-slate-400">Nhập mã hex, ví dụ <code class="text-fuchsia-200">#FF007F</code></p>
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

.color-field__palette,
.color-field__code {
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.03);
  padding: 0.85rem;
}

.color-field--compact .color-field__palette {
  padding: 0.65rem;
}

.color-field__picker-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.color-field__picker-shell {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  position: relative;
}

.color-field__swatch {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.85rem;
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.12);
}

.color-field--compact .color-field__swatch {
  width: 2rem;
  height: 2rem;
  border-radius: 0.65rem;
}

.color-field__picker {
  position: absolute;
  inset: 0;
  width: 2.5rem;
  height: 2.5rem;
  opacity: 0;
  cursor: pointer;
}

.color-field--compact .color-field__picker {
  width: 2rem;
  height: 2rem;
}

.color-field__current {
  font-size: 0.8rem;
  color: #e9d5ff;
}

.color-field__preset-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0.5rem;
  margin-bottom: 0.85rem;
}

.color-field--compact .color-field__preset-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.4rem;
  margin-bottom: 0.65rem;
}

.color-field__preset {
  aspect-ratio: 1;
  border-radius: 0.75rem;
  border: 2px solid transparent;
  cursor: pointer;
}

.color-field--compact .color-field__preset {
  border-radius: 0.55rem;
}

.color-field__preset--active {
  border-color: #f5d0fe;
  box-shadow: 0 0 0 2px rgba(217, 70, 239, 0.35);
}
</style>
