<script setup lang="ts">
import { computed } from 'vue'

import {
  buildProfileSurfaceStyle,
  contrastTextOn,
  profileAccentVars,
} from '../../lib/profileTheme'

const props = defineProps<{
  displayName?: string | null
  username?: string | null
  bio?: string | null
  avatarUrl?: string | null
  avatarStyle?: string | null
  primaryColor?: string | null
  textColor?: string | null
  fontFamily?: string | null
  bgType?: string | null
  bgValue?: string | null
  buttonStyle?: string | null
  phone?: string | null
  zalo?: string | null
  messenger?: string | null
  fallbackInitial?: string
}>()

const surfaceStyle = computed(() => ({
  ...buildProfileSurfaceStyle({
    bg_type: props.bgType,
    bg_value: props.bgValue,
    text_color: props.textColor,
    font_family: props.fontFamily,
  }),
  ...profileAccentVars(props.primaryColor),
}))

const avatarRadiusClass = computed(() => {
  return {
    circle: 'rounded-full',
    square: 'rounded-none',
    rounded: 'rounded-3xl',
  }[props.avatarStyle || 'rounded']
})

const buttonStyle = computed(() => {
  const primary = props.primaryColor || '#8B5CF6'
  const style = props.buttonStyle || 'filled'
  const labelColor = contrastTextOn(primary)

  if (style === 'outline') {
    return {
      color: primary,
      backgroundColor: 'transparent',
      borderColor: primary,
    }
  }

  return {
    color: labelColor,
    backgroundColor: primary,
    borderColor: 'transparent',
    boxShadow: style === 'shadow' ? '0 16px 32px rgba(15, 23, 42, 0.28)' : undefined,
  }
})

const contacts = computed(() => {
  const items: Array<{ label: string; value: string }> = []
  if (props.phone) items.push({ label: 'Phone', value: props.phone })
  if (props.zalo) items.push({ label: 'Zalo', value: props.zalo })
  if (props.messenger) items.push({ label: 'Messenger', value: props.messenger })
  return items
})
</script>

<template>
  <div class="profile-preview" :style="surfaceStyle">
    <div class="profile-preview__scrim" />

    <div class="profile-preview__content">
      <div class="profile-preview__hero">
        <img
          v-if="avatarUrl"
          :src="avatarUrl"
          alt="avatar"
          class="profile-preview__avatar object-cover"
          :class="avatarRadiusClass"
        />
        <div
          v-else
          class="profile-preview__avatar profile-preview__avatar-fallback"
          :class="avatarRadiusClass"
        >
          {{ fallbackInitial || displayName?.slice(0, 1)?.toUpperCase() || 'C' }}
        </div>

        <div class="min-w-0 flex-1">
          <p class="profile-preview__eyebrow">Public profile</p>
          <h4 class="profile-preview__title">{{ displayName || 'Your display name' }}</h4>
          <p class="profile-preview__handle">@{{ username || 'username' }}</p>
        </div>
      </div>

      <p class="profile-preview__bio">
        {{ bio || 'Use the form to define your public bio, contact details, and branding.' }}
      </p>

      <div v-if="contacts.length" class="profile-preview__contacts">
        <span
          v-for="contact in contacts"
          :key="contact.label"
          class="profile-preview__chip"
          :class="{ 'profile-preview__chip--accent': contact.label === 'Phone' }"
        >
          <span class="profile-preview__chip-label">{{ contact.label }}</span>
          <span>{{ contact.value }}</span>
        </span>
      </div>

      <div class="profile-preview__actions">
        <button class="profile-preview__button" type="button" :style="buttonStyle">
          Book collaboration
        </button>
        <span class="profile-preview__ghost">Preview only</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-preview {
  position: relative;
  overflow: hidden;
  border-radius: 1.75rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 24px 60px rgba(2, 6, 23, 0.28);
}

.profile-preview__scrim {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(15, 23, 42, 0.08));
  pointer-events: none;
}

.profile-preview__content {
  position: relative;
  padding: 1.35rem;
  color: inherit;
}

.profile-preview__hero {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.profile-preview__avatar {
  width: 4.75rem;
  height: 4.75rem;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.18);
}

.profile-preview__avatar-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.12);
  font-size: 1.5rem;
  font-weight: 700;
}

.profile-preview__eyebrow {
  font-size: 0.72rem;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  opacity: 0.68;
}

.profile-preview__title {
  margin-top: 0.45rem;
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.2;
}

.profile-preview__handle {
  margin-top: 0.2rem;
  font-size: 0.9rem;
  opacity: 0.72;
}

.profile-preview__bio {
  margin-top: 1rem;
  font-size: 0.92rem;
  line-height: 1.7;
  opacity: 0.88;
}

.profile-preview__contacts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-top: 1rem;
}

.profile-preview__chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, currentColor 18%, transparent);
  background: color-mix(in srgb, currentColor 8%, transparent);
  padding: 0.4rem 0.75rem;
  font-size: 0.76rem;
  font-weight: 600;
}

.profile-preview__chip--accent {
  border-color: var(--profile-accent-border);
  background: var(--profile-accent-soft);
  color: var(--profile-accent);
}

.profile-preview__chip-label {
  opacity: 0.72;
  font-weight: 500;
}

.profile-preview__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1.15rem;
}

.profile-preview__button {
  border-radius: 999px;
  border: 1px solid transparent;
  padding: 0.72rem 1.15rem;
  font-size: 0.88rem;
  font-weight: 700;
}

.profile-preview__ghost {
  font-size: 0.75rem;
  opacity: 0.55;
}
</style>
