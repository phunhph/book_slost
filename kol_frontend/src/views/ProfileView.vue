<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { publicProfileUrl as buildPublicProfileUrl } from '../lib/appUrls'
import { resolveThemeForBackground } from '../lib/colorUtils'
import { defaultLayoutV2, migrateLayoutToV2, normalizeLayoutV2, parseLayout } from '../lib/profileBlocks'
import { buildDemoLayoutV2, DEMO_AVATAR_URL, DEMO_PROFILE_COPY, DEMO_THEME } from '../lib/profileDemoContent'
import { getProfileByUser, updateProfileByUser } from '../services/api'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import BackgroundField from '../components/ui/BackgroundField.vue'
import ColorField from '../components/ui/ColorField.vue'
import ProfileLayoutBuilder from '../components/profile/ProfileLayoutBuilder.vue'
import ProfilePageRenderer from '../components/profile/ProfilePageRenderer.vue'
import { withResolvedProfileTheme } from '../lib/profileTheme'
import type { ProfileLayoutV2, ProfileUpdatePayload, UserProfile } from '../types'

const auth = useAuthStore()
const toast = useToastStore()
const loading = ref(true)
const saving = ref(false)
const activeTab = ref<'identity' | 'theme' | 'blocks' | 'preview'>('identity')

const tabs = [
  { id: 'identity' as const, label: 'Thông tin', hint: 'Tên, avatar, liên hệ' },
  { id: 'theme' as const, label: 'Giao diện', hint: 'Màu sắc, nền, font' },
  { id: 'blocks' as const, label: 'Nội dung trang', hint: 'Blocks & landing page' },
  { id: 'preview' as const, label: 'Xem trước', hint: 'Public page' },
]

const form = reactive<ProfileUpdatePayload>({
  username: null,
  display_name: null,
  bio: null,
  avatar_url: null,
  theme_mode: 'dark',
  font_family: 'Inter',
  primary_color: '#8b5cf6',
  text_color: '#f8fafc',
  bg_type: 'gradient',
  bg_value: null,
  avatar_style: 'rounded',
  button_style: 'filled',
  phone: null,
  zalo: null,
  messenger: null,
  layout_structure: defaultLayoutV2(),
})

const themeModeOptions = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'custom', label: 'Custom' },
]

const bgTypeOptions = [
  { value: 'color', label: 'Solid color' },
  { value: 'gradient', label: 'Gradient' },
  { value: 'image', label: 'Image URL' },
]

const avatarStyleOptions = [
  { value: 'circle', label: 'Circle' },
  { value: 'square', label: 'Square' },
  { value: 'rounded', label: 'Rounded' },
]

const buttonStyleOptions = [
  { value: 'filled', label: 'Filled' },
  { value: 'outline', label: 'Outline' },
  { value: 'shadow', label: 'Shadow' },
]

const fontFamilyOptions = [
  'Inter',
  'Roboto',
  'Poppins',
  'Montserrat',
  'Playfair Display',
  'Merriweather',
  'Be Vietnam Pro',
]

const publicProfileLink = computed(() => {
  if (!form.username) return null
  return buildPublicProfileUrl(form.username)
})

const layoutModel = computed({
  get: () =>
    migrateLayoutToV2(form.layout_structure, {
      bio: form.bio ?? undefined,
      phone: form.phone,
      zalo: form.zalo,
      messenger: form.messenger,
    }),
  set: (value: ProfileLayoutV2) => {
    form.layout_structure = normalizeLayoutV2(value)
  },
})

const previewProfile = computed((): UserProfile =>
  withResolvedProfileTheme({
    user_id: auth.user?.id ?? '',
    username: form.username ?? null,
    display_name: form.display_name ?? null,
    bio: form.bio ?? null,
    avatar_url: form.avatar_url ?? null,
    theme_mode: form.theme_mode ?? 'dark',
    font_family: form.font_family ?? 'Inter',
    primary_color: form.primary_color ?? '#8b5cf6',
    text_color: form.text_color ?? '#f8fafc',
    bg_type: form.bg_type ?? 'gradient',
    bg_value: form.bg_value ?? null,
    avatar_style: form.avatar_style ?? 'rounded',
    button_style: form.button_style ?? 'filled',
    phone: form.phone ?? null,
    zalo: form.zalo ?? null,
    messenger: form.messenger ?? null,
    layout_structure: layoutModel.value,
    created_at: '',
    updated_at: '',
  }),
)

function applyProfile(profile: UserProfile) {
  form.username = profile.username
  form.display_name = profile.display_name
  form.bio = profile.bio
  form.avatar_url = profile.avatar_url
  form.theme_mode = profile.theme_mode
  form.font_family = profile.font_family
  form.primary_color = profile.primary_color
  form.text_color = profile.text_color
  form.bg_type = profile.bg_type
  form.bg_value = profile.bg_value
  form.avatar_style = profile.avatar_style
  form.button_style = profile.button_style
  form.phone = profile.phone
  form.zalo = profile.zalo
  form.messenger = profile.messenger
  form.layout_structure = parseLayout(profile)
}

function buildSavePayload(): ProfileUpdatePayload {
  if (form.bg_type === 'gradient') {
    syncThemeFromBackground()
  }

  const payload: ProfileUpdatePayload = {
    layout_structure: normalizeLayoutV2(layoutModel.value),
  }

  const scalarFields = [
    'username',
    'display_name',
    'bio',
    'avatar_url',
    'theme_mode',
    'font_family',
    'primary_color',
    'text_color',
    'bg_type',
    'bg_value',
    'avatar_style',
    'button_style',
    'phone',
    'zalo',
    'messenger',
  ] as const

  for (const field of scalarFields) {
    const value = form[field]
    if (value !== null && value !== undefined && value !== '') {
      payload[field] = value
    }
  }

  return payload
}

function applyThemeFromBackground(theme: { textColor: string; primaryColor: string }) {
  form.text_color = theme.textColor
  form.primary_color = theme.primaryColor
}

function syncThemeFromBackground() {
  const theme = resolveThemeForBackground(form.bg_type, form.bg_value)
  if (!theme) return
  form.text_color = theme.textColor
  form.primary_color = theme.primaryColor
}

watch(
  () => form.bg_value,
  () => {
    if (form.bg_type === 'gradient') {
      syncThemeFromBackground()
    }
  },
)

function fillDemoContent() {
  form.bio = DEMO_PROFILE_COPY.bio
  form.phone = DEMO_PROFILE_COPY.phone
  form.zalo = DEMO_PROFILE_COPY.zalo
  form.messenger = DEMO_PROFILE_COPY.messenger
  form.avatar_url = DEMO_AVATAR_URL
  form.text_color = DEMO_THEME.text_color
  form.primary_color = DEMO_THEME.primary_color
  form.bg_type = DEMO_THEME.bg_type
  form.bg_value = DEMO_THEME.bg_value
  form.layout_structure = buildDemoLayoutV2()
  toast.info('Đã điền nội dung mẫu. Nhấn Save profile để lưu.')
}

async function loadProfile() {
  if (!auth.user) return
  loading.value = true

  try {
    const profile = await getProfileByUser(auth.user.id)
    applyProfile(profile)
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Unable to load profile.')
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  if (!auth.user) return
  saving.value = true

  try {
    const profile = await updateProfileByUser(auth.user.id, buildSavePayload())
    applyProfile(profile)
    toast.success('Profile updated successfully.')
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.data?.detail) {
      const detail = error.response.data.detail
      toast.error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    } else {
      toast.error(error instanceof Error ? error.message : 'Unable to save profile.')
    }
  } finally {
    saving.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <div class="profile-workspace mx-auto max-w-5xl space-y-5">
    <header class="glass-panel page-panel flex flex-wrap items-start justify-between gap-4 rounded-[2rem]">
      <div>
        <p class="text-sm uppercase tracking-[0.3em] text-violet-300/80">Profile studio</p>
        <h2 class="mt-2 text-2xl font-semibold text-white">Tùy chỉnh trang công khai</h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
          Chỉnh thông tin, giao diện và nội dung trang public của bạn.
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <a
          v-if="publicProfileLink"
          :href="publicProfileLink"
          target="_blank"
          rel="noreferrer"
          class="btn-secondary text-sm"
        >
          Mở trang public
        </a>
        <button class="btn-secondary text-sm" type="button" @click="activeTab = 'preview'">
          Xem trước
        </button>
        <button class="btn-primary text-sm" type="button" :disabled="saving || loading" @click="saveProfile">
          {{ saving ? 'Đang lưu...' : 'Lưu profile' }}
        </button>
      </div>
    </header>

    <nav class="profile-workspace-tabs" aria-label="Profile sections">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="profile-workspace-tab"
        :class="{ 'profile-workspace-tab--active': activeTab === tab.id }"
        type="button"
        @click="activeTab = tab.id"
      >
        <span class="profile-workspace-tab__label">{{ tab.label }}</span>
        <span class="profile-workspace-tab__hint">{{ tab.hint }}</span>
      </button>
    </nav>

    <div v-if="loading" class="glass-panel page-panel rounded-[2rem] p-6 text-sm text-slate-400">Đang tải profile...</div>

    <form v-else class="space-y-5" @submit.prevent="saveProfile">
      <section v-show="activeTab === 'identity'" class="glass-panel page-panel rounded-[2rem]">
        <p class="profile-form-section__title">Thông tin cơ bản</p>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <div>
            <label class="mb-2 block text-sm text-slate-300">Display name</label>
            <input v-model="form.display_name" class="field" type="text" placeholder="Tên hiển thị" />
          </div>
          <div>
            <label class="mb-2 block text-sm text-slate-300">Username</label>
            <input v-model="form.username" class="field" type="text" placeholder="creator-demo" />
          </div>
          <div class="md:col-span-2">
            <label class="mb-2 block text-sm text-slate-300">Bio ngắn (hero)</label>
            <textarea v-model="form.bio" class="field min-h-28" placeholder="Giới thiệu ngắn về bạn..." />
          </div>
          <div class="md:col-span-2">
            <label class="mb-2 block text-sm text-slate-300">Avatar URL</label>
            <input v-model="form.avatar_url" class="field min-w-0" type="url" placeholder="https://..." />
          </div>
          <div>
            <label class="mb-2 block text-sm text-slate-300">Phone</label>
            <input v-model="form.phone" class="field" type="text" placeholder="0901000001" />
          </div>
          <div>
            <label class="mb-2 block text-sm text-slate-300">Zalo</label>
            <input v-model="form.zalo" class="field" type="text" placeholder="Zalo ID" />
          </div>
          <div class="md:col-span-2">
            <label class="mb-2 block text-sm text-slate-300">Messenger</label>
            <input v-model="form.messenger" class="field" type="text" placeholder="Facebook / Messenger" />
          </div>
        </div>
      </section>

      <section v-show="activeTab === 'theme'" class="glass-panel page-panel rounded-[2rem]">
        <p class="profile-form-section__title">Giao diện & màu sắc</p>
        <div class="mt-4 grid gap-5 lg:grid-cols-2 lg:items-start">
          <ColorField
            :model-value="form.primary_color || '#FF007F'"
            label="Màu chính (Primary)"
            @update:model-value="form.primary_color = $event"
          />
          <ColorField
            :model-value="form.text_color || '#111111'"
            label="Màu chữ (Text)"
            @update:model-value="form.text_color = $event"
          />
          <div>
            <label class="mb-2 block text-sm text-slate-300">Theme mode</label>
            <select v-model="form.theme_mode" class="field">
              <option v-for="option in themeModeOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="mb-2 block text-sm text-slate-300">Font chữ</label>
            <select v-model="form.font_family" class="field">
              <option v-for="font in fontFamilyOptions" :key="font" :value="font">{{ font }}</option>
            </select>
          </div>
          <div>
            <label class="mb-2 block text-sm text-slate-300">Background type</label>
            <select v-model="form.bg_type" class="field">
              <option v-for="option in bgTypeOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="mb-2 block text-sm text-slate-300">Avatar style</label>
            <select v-model="form.avatar_style" class="field">
              <option v-for="option in avatarStyleOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          <BackgroundField
            class="lg:col-span-2"
            :model-value="form.bg_value"
            :bg-type="form.bg_type"
            @update:model-value="form.bg_value = $event"
            @apply-theme="applyThemeFromBackground"
          />
          <div>
            <label class="mb-2 block text-sm text-slate-300">Button style</label>
            <select v-model="form.button_style" class="field">
              <option v-for="option in buttonStyleOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
        </div>
      </section>

      <section v-show="activeTab === 'blocks'" class="glass-panel page-panel rounded-[2rem]">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <p class="profile-form-section__title !mb-0">Nội dung trang</p>
          <button class="btn-secondary text-sm" type="button" @click="fillDemoContent">
            Điền nội dung mẫu
          </button>
        </div>
        <div class="mt-5">
          <ProfileLayoutBuilder v-model="layoutModel" />
        </div>
      </section>

      <section v-show="activeTab === 'preview'" class="glass-panel page-panel overflow-hidden rounded-[2rem]">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <p class="profile-form-section__title !mb-1">Live preview</p>
            <p class="text-sm text-slate-400">Đây là trang public khách hàng sẽ thấy.</p>
          </div>
          <a
            v-if="publicProfileLink"
            :href="publicProfileLink"
            target="_blank"
            rel="noreferrer"
            class="btn-secondary text-sm"
          >
            Mở tab mới
          </a>
        </div>
        <div class="overflow-hidden rounded-2xl border border-white/8 bg-black/25">
          <ProfilePageRenderer :profile="previewProfile" preview />
        </div>
      </section>

      <div class="profile-workspace-footer flex flex-wrap items-center justify-between gap-3">
        <p class="text-sm text-slate-400">Nhớ bấm <strong class="text-slate-200">Lưu profile</strong> sau khi chỉnh xong.</p>
        <button class="btn-primary" type="submit" :disabled="saving">
          {{ saving ? 'Đang lưu...' : 'Lưu profile' }}
        </button>
      </div>
    </form>
  </div>
</template>
