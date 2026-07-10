<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { publicProfileUrl as buildPublicProfileUrl } from '../lib/appUrls'
import { VN_BANKS, bankNameFromCode } from '../lib/banks'
import { defaultLayoutV2, migrateLayoutToV2, normalizeLayoutV2, parseLayout } from '../lib/profileBlocks'
import { buildDemoLayoutV2, DEMO_AVATAR_URL, DEMO_PROFILE_COPY, DEMO_THEME } from '../lib/profileDemoContent'
import { getProfileByUser, updateProfileByUser } from '../services/api'
import { getErrorMessage } from '../utils/errors'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import BackgroundField from '../components/ui/BackgroundField.vue'
import ColorField from '../components/ui/ColorField.vue'
import ProfileConnectionsEditor from '../components/profile/ProfileConnectionsEditor.vue'
import ProfileLayoutBuilder from '../components/profile/ProfileLayoutBuilder.vue'
import ProfilePageRenderer from '../components/profile/ProfilePageRenderer.vue'
import { withResolvedProfileTheme } from '../lib/profileTheme'
import type { ProfileLayoutV2, ProfileUpdatePayload, UserProfile } from '../types'

const auth = useAuthStore()
const toast = useToastStore()
const loading = ref(true)
const saving = ref(false)
const activeTab = ref<'identity' | 'connect' | 'theme' | 'content' | 'preview'>('identity')
const fieldErrors = reactive<Record<string, string>>({})
const touched = reactive<Record<string, boolean>>({})

const tabs = [
  { id: 'identity' as const, label: 'Hồ sơ', hint: 'Tên, giá, ngân hàng' },
  { id: 'connect' as const, label: 'Kết nối', hint: 'Liên hệ & MXH' },
  { id: 'theme' as const, label: 'Giao diện', hint: 'Màu, font, nền' },
  { id: 'content' as const, label: 'Nội dung', hint: 'Giới thiệu, ảnh, lịch' },
  { id: 'preview' as const, label: 'Xem trước', hint: 'Trang công khai' },
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
  contact_links: [],
  pricing_type: 'match',
  price_per_match: 150000,
  price_per_hour: 100000,
  currency: 'VND',
  bank_name: null,
  bank_code: '',
  bank_account_number: null,
  bank_account_name: null,
  layout_structure: defaultLayoutV2(),
})

const themeModeOptions = [
  { value: 'light', label: 'Sáng' },
  { value: 'dark', label: 'Tối' },
  { value: 'custom', label: 'Tùy chỉnh' },
]

const bgTypeOptions = [
  { value: 'color', label: 'Màu đặc' },
  { value: 'gradient', label: 'Gradient' },
  { value: 'image', label: 'URL ảnh' },
]

const avatarStyleOptions = [
  { value: 'circle', label: 'Tròn' },
  { value: 'square', label: 'Vuông' },
  { value: 'rounded', label: 'Bo góc' },
]

const buttonStyleOptions = [
  { value: 'filled', label: 'Đổ đầy' },
  { value: 'outline', label: 'Viền' },
  { value: 'shadow', label: 'Đổ bóng' },
]

const pricingTypeOptions = [
  { value: 'match', label: 'Theo trận' },
  { value: 'hourly', label: 'Theo giờ' },
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

const hasBankConfigured = computed(() =>
  Boolean(form.bank_code?.trim() && form.bank_account_number?.trim() && form.bank_account_name?.trim()),
)

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

const themeEditSubMode = ref<'presets' | 'custom'>('presets')

const themePresets = [
  {
    label: 'Pink Sky',
    value: 'linear-gradient(135deg, #FDF2F8 0%, #E0F2FE 100%)',
    textColor: '#0F172A',
    primaryColor: '#DB2777',
    vibe: 'Cute / Đáng yêu',
    themeMode: 'light',
  },
  {
    label: 'Strawberry Cream',
    value: 'linear-gradient(135deg, #FFF0F6 0%, #FCC2D7 100%)',
    textColor: '#4D052E',
    primaryColor: '#D01257',
    vibe: 'Cute / Đáng yêu',
    themeMode: 'light',
  },
  {
    label: 'Soft Yellow Cream',
    value: 'linear-gradient(135deg, #FFF9DB 0%, #FFF3BF 100%)',
    textColor: '#5C3E00',
    primaryColor: '#D97706',
    vibe: 'Cute / Đáng yêu',
    themeMode: 'light',
  },
  {
    label: 'Sweet Peach',
    value: 'linear-gradient(135deg, #FFECE0 0%, #FFF5F0 100%)',
    textColor: '#5B2100',
    primaryColor: '#E04F1D',
    vibe: 'Cute / Đáng yêu',
    themeMode: 'light',
  },
  {
    label: 'Deep Ocean Blue',
    value: 'linear-gradient(135deg, #0B0F19 0%, #0F172A 100%)',
    textColor: '#F8FAFC',
    primaryColor: '#3B82F6',
    vibe: 'Nam tính',
    themeMode: 'dark',
  },
  {
    label: 'Polar Light',
    value: 'linear-gradient(135deg, #020617 0%, #083344 100%)',
    textColor: '#E0F2FE',
    primaryColor: '#06B6D4',
    vibe: 'Nam tính',
    themeMode: 'dark',
  },
  {
    label: 'Stealth Grey',
    value: 'linear-gradient(135deg, #09090B 0%, #18181B 50%, #27272A 100%)',
    textColor: '#F4F4F5',
    primaryColor: '#A1A1AA',
    vibe: 'Nam tính',
    themeMode: 'dark',
  },
  {
    label: 'Carbon Shadow',
    value: 'linear-gradient(135deg, #030712 0%, #1F2937 100%)',
    textColor: '#F9FAFB',
    primaryColor: '#6366F1',
    vibe: 'Nam tính',
    themeMode: 'dark',
  },
  {
    label: 'Elegant Violet',
    value: 'linear-gradient(135deg, #FAF5FF 0%, #F3E8FF 100%)',
    textColor: '#3B0764',
    primaryColor: '#9333EA',
    vibe: 'Nữ tính',
    themeMode: 'light',
  },
  {
    label: 'Lavender Dream',
    value: 'linear-gradient(135deg, #F3E8FF 0%, #E8D5B5 100%)',
    textColor: '#2E1065',
    primaryColor: '#D946EF',
    vibe: 'Nữ tính',
    themeMode: 'light',
  },
  {
    label: 'Cherry Blossom',
    value: 'linear-gradient(135deg, #FFF5F7 0%, #FCE7F3 100%)',
    textColor: '#500730',
    primaryColor: '#EC4899',
    vibe: 'Nữ tính',
    themeMode: 'light',
  },
  {
    label: 'Cosmic Orchid',
    value: 'linear-gradient(135deg, #2E1065 0%, #4C1D95 100%)',
    textColor: '#F5F3FF',
    primaryColor: '#C084FC',
    vibe: 'Nữ tính',
    themeMode: 'dark',
  },
  {
    label: 'Cyberpunk Purple',
    value: 'linear-gradient(135deg, #090514 0%, #1F104F 100%)',
    textColor: '#F5F3FF',
    primaryColor: '#39FF14',
    vibe: 'Cyberpunk / Gaming',
    themeMode: 'dark',
  },
  {
    label: 'Acid Lime Green',
    value: 'linear-gradient(135deg, #180022 0%, #300044 100%)',
    textColor: '#FDF4FF',
    primaryColor: '#CCFF00',
    vibe: 'Cyberpunk / Gaming',
    themeMode: 'dark',
  },
  {
    label: 'Night City Neon',
    value: 'linear-gradient(135deg, #03001e 0%, #7303c0 50%, #ec38bc 100%)',
    textColor: '#FFFFFF',
    primaryColor: '#00F0FF',
    vibe: 'Cyberpunk / Gaming',
    themeMode: 'dark',
  },
  {
    label: 'Solar Explosion',
    value: 'linear-gradient(135deg, #110404 0%, #3F0712 100%)',
    textColor: '#FFF5F5',
    primaryColor: '#FF3F00',
    vibe: 'Cyberpunk / Gaming',
    themeMode: 'dark',
  },
]

function applyPreset(preset: typeof themePresets[0]) {
  form.bg_type = 'gradient'
  form.bg_value = preset.value
  form.primary_color = preset.primaryColor
  form.text_color = preset.textColor
  form.theme_mode = preset.themeMode
  toast.success(`Đã áp dụng vibe màu "${preset.label}"!`)
}


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
    pricing_type: form.pricing_type ?? 'match',
    price_per_match: form.price_per_match ?? 0,
    price_per_hour: form.price_per_hour ?? 0,
    currency: form.currency ?? 'VND',
    bank_name: form.bank_name ?? null,
    bank_code: form.bank_code ?? null,
    bank_account_number: form.bank_account_number ?? null,
    bank_account_name: form.bank_account_name ?? null,
    layout_structure: layoutModel.value,
    created_at: '',
    updated_at: '',
  }),
)

function clearFieldError(field: string) {
  delete fieldErrors[field]
}

function markTouched(field: string) {
  touched[field] = true
  validateField(field)
}

function validateField(field: string): string {
  let message = ''
  const username = (form.username || '').trim()
  const phone = (form.phone || '').trim()
  const bankCode = (form.bank_code || '').trim()
  const bankAccountNumber = (form.bank_account_number || '').replace(/\s+/g, '')
  const bankAccountName = (form.bank_account_name || '').trim()
  const anyBankValue = Boolean(bankCode || bankAccountNumber || bankAccountName || (form.bank_name || '').trim())

  if (field === 'username') {
    if (!username) message = 'Vui lòng nhập username công khai.'
    else if (username.length < 3) message = 'Username tối thiểu 3 ký tự.'
    else if (!/^[a-zA-Z0-9._-]+$/.test(username)) message = 'Username chỉ gồm chữ, số, dấu chấm, gạch dưới, gạch ngang.'
  }

  if (field === 'display_name' && !(form.display_name || '').trim()) {
    message = 'Vui lòng nhập tên hiển thị.'
  }

  if (field === 'phone' && phone && !/^(0|\+84)\d{8,10}$/.test(phone.replace(/[\s.-]/g, ''))) {
    message = 'Số điện thoại không hợp lệ (ví dụ 0901234567).'
  }

  if (field === 'price_per_match') {
    if ((form.price_per_match ?? 0) < 0) message = 'Giá theo trận không được âm.'
  }

  if (field === 'price_per_hour') {
    if ((form.price_per_hour ?? 0) < 0) message = 'Giá theo giờ không được âm.'
  }

  if (field === 'bank_code' && anyBankValue && !bankCode) {
    message = 'Chọn ngân hàng để tạo mã QR VietQR.'
  }

  if (field === 'bank_account_number') {
    if (anyBankValue && !bankAccountNumber) message = 'Vui lòng nhập số tài khoản.'
    else if (bankAccountNumber && !/^\d{6,20}$/.test(bankAccountNumber)) {
      message = 'Số tài khoản phải gồm 6–20 chữ số.'
    }
  }

  if (field === 'bank_account_name') {
    if (anyBankValue && !bankAccountName) message = 'Vui lòng nhập tên chủ tài khoản.'
    else if (bankAccountName && bankAccountName.length < 3) message = 'Tên chủ tài khoản quá ngắn.'
  }

  if (message) fieldErrors[field] = message
  else clearFieldError(field)
  return message
}

function validateProfileForm(): boolean {
  const fields = [
    'username',
    'display_name',
    'phone',
    'price_per_match',
    'price_per_hour',
    'bank_code',
    'bank_account_number',
    'bank_account_name',
  ]
  let ok = true
  for (const field of fields) {
    touched[field] = true
    if (validateField(field)) ok = false
  }

  if ((form.price_per_match ?? 0) <= 0 && (form.price_per_hour ?? 0) <= 0) {
    fieldErrors.price_per_match = 'Cần ít nhất một mức giá > 0 (theo trận hoặc theo giờ).'
    fieldErrors.price_per_hour = 'Cần ít nhất một mức giá > 0 (theo trận hoặc theo giờ).'
    ok = false
  }

  return ok
}

function fieldClass(field: string) {
  return [
    'field',
    touched[field] && fieldErrors[field] ? 'field--error' : '',
  ]
}

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
  form.contact_links = profile.contact_links || []
  form.pricing_type = profile.pricing_type || 'match'
  form.price_per_match = profile.price_per_match ?? 0
  form.price_per_hour = profile.price_per_hour ?? 0
  form.currency = profile.currency || 'VND'
  form.bank_name = profile.bank_name
  form.bank_code = profile.bank_code || ''
  form.bank_account_number = profile.bank_account_number
  form.bank_account_name = profile.bank_account_name
  form.layout_structure = parseLayout(profile)
}

function buildSavePayload(): ProfileUpdatePayload {
  const payload: ProfileUpdatePayload = {
    layout_structure: normalizeLayoutV2(layoutModel.value),
    pricing_type: form.pricing_type ?? 'match',
    price_per_match: form.price_per_match ?? 0,
    price_per_hour: form.price_per_hour ?? 0,
    currency: form.currency || 'VND',
    bank_code: (form.bank_code || '').trim() || null,
    bank_name: bankNameFromCode(form.bank_code) || (form.bank_name || '').trim() || null,
    bank_account_number: (form.bank_account_number || '').replace(/\s+/g, '') || null,
    bank_account_name: (form.bank_account_name || '').trim().toUpperCase() || null,
    contact_links: form.contact_links || [],
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
  toast.info('Đã điền nội dung mẫu. Nhấn Lưu profile để lưu.')
}

async function loadProfile() {
  if (!auth.user) return
  loading.value = true

  try {
    const profile = await getProfileByUser(auth.user.id)
    applyProfile(profile)
  } catch (error) {
    toast.error(getErrorMessage(error, 'Không tải được hồ sơ.'))
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  if (!auth.user) return

  if (!validateProfileForm()) {
    activeTab.value = 'identity'
    toast.error('Vui lòng sửa các ô đang báo lỗi trước khi lưu.')
    return
  }

  saving.value = true

  try {
    const profile = await updateProfileByUser(auth.user.id, buildSavePayload())
    applyProfile(profile)
    toast.success(
      hasBankConfigured.value
        ? 'Cập nhật hồ sơ thành công. Đã sẵn sàng tạo mã QR thanh toán.'
        : 'Cập nhật hồ sơ thành công. Hãy thêm tài khoản ngân hàng để tạo mã QR.',
    )
  } catch (error) {
    toast.error(getErrorMessage(error, 'Không lưu được hồ sơ.'))
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
        <p class="text-sm uppercase tracking-[0.3em] text-violet-300/80">Studio hồ sơ</p>
        <h2 class="mt-2 text-2xl font-semibold text-white">Tùy chỉnh trang công khai</h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
          Chỉnh thông tin, giao diện và nội dung trang công khai của bạn.
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
          Mở trang công khai
        </a>
        <button class="btn-secondary text-sm" type="button" @click="activeTab = 'preview'">
          Xem trước
        </button>
        <button class="btn-primary text-sm" type="button" :disabled="saving || loading" @click="saveProfile">
          {{ saving ? 'Đang lưu...' : 'Lưu profile' }}
        </button>
      </div>
    </header>

    <nav class="profile-workspace-tabs" aria-label="Các phần hồ sơ">
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

    <div v-if="loading" class="glass-panel page-panel rounded-[2rem] p-6 text-sm text-slate-400">Đang tải hồ sơ...</div>

    <form v-else class="space-y-5" @submit.prevent="saveProfile">
      <section v-show="activeTab === 'identity'" class="glass-panel page-panel rounded-[2rem]">
        <p class="profile-form-section__title">Thông tin cơ bản</p>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <div>
            <label class="mb-2 block text-sm text-slate-300">Tên hiển thị *</label>
            <input
              v-model="form.display_name"
              :class="fieldClass('display_name')"
              type="text"
              placeholder="Tên hiển thị"
              @blur="markTouched('display_name')"
              @input="validateField('display_name')"
            />
            <p v-if="touched.display_name && fieldErrors.display_name" class="field-error">{{ fieldErrors.display_name }}</p>
          </div>
          <div>
            <label class="mb-2 block text-sm text-slate-300">Username *</label>
            <input
              v-model="form.username"
              :class="fieldClass('username')"
              type="text"
              placeholder="creator-demo"
              @blur="markTouched('username')"
              @input="validateField('username')"
            />
            <p v-if="touched.username && fieldErrors.username" class="field-error">{{ fieldErrors.username }}</p>
          </div>
          <div class="md:col-span-2">
            <label class="mb-2 block text-sm text-slate-300">Bio ngắn (hero)</label>
            <textarea v-model="form.bio" class="field min-h-28" placeholder="Giới thiệu ngắn về bạn..." />
          </div>
          <div class="md:col-span-2">
            <label class="mb-2 block text-sm text-slate-300">URL avatar</label>
            <input v-model="form.avatar_url" class="field min-w-0" type="url" placeholder="https://..." />
          </div>
          <div>
            <label class="mb-2 block text-sm text-slate-300">Kiểu giá mặc định</label>
            <select v-model="form.pricing_type" class="field">
              <option v-for="option in pricingTypeOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="mb-2 block text-sm text-slate-300">Đơn vị tiền</label>
            <input v-model="form.currency" class="field" type="text" placeholder="VND" />
          </div>
          <div>
            <label class="mb-2 block text-sm text-slate-300">Giá theo trận (VND) *</label>
            <input
              v-model.number="form.price_per_match"
              :class="fieldClass('price_per_match')"
              min="0"
              type="number"
              placeholder="150000"
              @blur="markTouched('price_per_match')"
              @input="validateField('price_per_match')"
            />
            <p v-if="touched.price_per_match && fieldErrors.price_per_match" class="field-error">{{ fieldErrors.price_per_match }}</p>
          </div>
          <div>
            <label class="mb-2 block text-sm text-slate-300">Giá theo giờ (VND) *</label>
            <input
              v-model.number="form.price_per_hour"
              :class="fieldClass('price_per_hour')"
              min="0"
              type="number"
              placeholder="100000"
              @blur="markTouched('price_per_hour')"
              @input="validateField('price_per_hour')"
            />
            <p v-if="touched.price_per_hour && fieldErrors.price_per_hour" class="field-error">{{ fieldErrors.price_per_hour }}</p>
          </div>
        </div>

        <div class="mt-8 border-t border-white/10 pt-6">
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p class="profile-form-section__title">Tài khoản nhận tiền (VietQR)</p>
              <p class="mt-2 text-sm text-slate-400">
                Bạn tự chọn ngân hàng và nhập STK của mình — không bị ép dùng một ngân hàng cố định.
                Khách sẽ chuyển khoản vào đúng STK này khi đặt lịch.
              </p>
            </div>
            <span
              class="rounded-full px-3 py-1 text-xs font-medium"
              :class="hasBankConfigured ? 'bg-emerald-500/15 text-emerald-200' : 'bg-amber-500/15 text-amber-200'"
            >
              {{ hasBankConfigured ? 'Đã cấu hình nhận tiền' : 'Chưa cấu hình nhận tiền' }}
            </span>
          </div>

          <div class="mt-4 grid gap-4 md:grid-cols-2">
            <div>
              <label class="mb-2 block text-sm text-slate-300">Ngân hàng của bạn *</label>
              <select
                v-model="form.bank_code"
                :class="fieldClass('bank_code')"
                @blur="markTouched('bank_code')"
                @change="validateField('bank_code'); validateField('bank_account_number'); validateField('bank_account_name')"
              >
                <option value="">Chọn ngân hàng bạn dùng</option>
                <option v-for="bank in VN_BANKS" :key="bank.code" :value="bank.code">
                  {{ bank.name }}
                </option>
              </select>
              <p v-if="touched.bank_code && fieldErrors.bank_code" class="field-error">{{ fieldErrors.bank_code }}</p>
            </div>
            <div>
              <label class="mb-2 block text-sm text-slate-300">Số tài khoản nhận tiền *</label>
              <input
                v-model="form.bank_account_number"
                :class="fieldClass('bank_account_number')"
                type="text"
                inputmode="numeric"
                placeholder="Nhập STK của bạn"
                @blur="markTouched('bank_account_number')"
                @input="validateField('bank_account_number')"
              />
              <p v-if="touched.bank_account_number && fieldErrors.bank_account_number" class="field-error">
                {{ fieldErrors.bank_account_number }}
              </p>
            </div>
            <div class="md:col-span-2">
              <label class="mb-2 block text-sm text-slate-300">Tên chủ tài khoản *</label>
              <input
                v-model="form.bank_account_name"
                :class="fieldClass('bank_account_name')"
                type="text"
                placeholder="NGUYEN VAN A"
                @blur="markTouched('bank_account_name')"
                @input="validateField('bank_account_name')"
              />
              <p v-if="touched.bank_account_name && fieldErrors.bank_account_name" class="field-error">
                {{ fieldErrors.bank_account_name }}
              </p>
              <p class="mt-2 text-xs text-slate-500">
                Viết hoa không dấu, khớp tên trên app ngân hàng của bạn. Mỗi KOL dùng STK riêng của mình.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section v-show="activeTab === 'connect'" class="glass-panel page-panel rounded-[2rem]">
        <p class="profile-form-section__title">Kết nối với khách</p>
        <p class="mt-2 text-sm text-slate-400">
          Các mục này hiển thị ngay dưới phần hero — khách thấy kênh liên hệ trước khi cuộn xuống nội dung dài.
        </p>
        <div class="mt-5">
          <ProfileConnectionsEditor
            v-model="layoutModel"
            v-model:phone="form.phone"
            v-model:zalo="form.zalo"
            v-model:messenger="form.messenger"
            v-model:contactLinks="form.contact_links"
          />
        </div>
      </section>

      <section v-show="activeTab === 'theme'" class="glass-panel page-panel rounded-[2rem]">
        <!-- Inner Sub-Tab switcher -->
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-white/8 pb-4 mb-5">
          <div>
            <p class="profile-form-section__title !mb-1">Thiết kế Giao diện</p>
            <p class="text-xs text-slate-400">Chọn theme phối sẵn hoặc tự do chỉnh sửa từng chi tiết.</p>
          </div>
          <div class="inline-flex gap-1 p-1 rounded-full border border-white/8 bg-black/30 shrink-0">
            <button
              type="button"
              class="px-4 py-2 rounded-full text-xs font-semibold transition cursor-pointer"
              :class="themeEditSubMode === 'presets' ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white' : 'text-slate-400 hover:text-white'"
              @click="themeEditSubMode = 'presets'"
            >
              Gợi ý (Vibe màu phối sẵn)
            </button>
            <button
              type="button"
              class="px-4 py-2 rounded-full text-xs font-semibold transition cursor-pointer"
              :class="themeEditSubMode === 'custom' ? 'bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white' : 'text-slate-400 hover:text-white'"
              @click="themeEditSubMode = 'custom'"
            >
              Tùy chỉnh thủ công
            </button>
          </div>
        </div>

        <!-- 1. GỢI Ý (Vibe màu phối sẵn) -->
        <div v-show="themeEditSubMode === 'presets'" class="space-y-6">
          <p class="text-sm text-slate-400">
            Mỗi vibe màu dưới đây đã được tinh chỉnh độ tương phản hoàn hảo giữa màu nền, màu chữ và màu nhấn.
          </p>

          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <button
              v-for="preset in themePresets"
              :key="preset.label"
              type="button"
              class="group relative text-left rounded-2xl border border-white/8 p-4 bg-slate-900/40 hover:border-violet-500/50 hover:bg-slate-900/60 transition-all duration-300 flex flex-col justify-between h-32 cursor-pointer shadow-md"
              @click="applyPreset(preset)"
            >
              <div>
                <span class="inline-block text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border border-white/10 bg-white/5 text-slate-300 mb-2">
                  {{ preset.vibe }}
                </span>
                <h4 class="text-sm font-bold text-white group-hover:text-violet-200 transition">{{ preset.label }}</h4>
              </div>
              
              <!-- Mini Preview of Gradient and Text -->
              <div class="w-full h-8 rounded-lg mt-2 overflow-hidden border border-white/10 flex items-center justify-between px-3" :style="{ background: preset.value }">
                <span class="text-[9px] font-bold" :style="{ color: preset.textColor }">Mẫu chữ</span>
                <div class="flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full border border-white/10" :style="{ background: preset.primaryColor }" />
                  <span class="text-[8px] opacity-70" :style="{ color: preset.textColor }">Màu nhấn</span>
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- 2. TÙY CHỈNH THỦ CÔNG -->
        <div v-show="themeEditSubMode === 'custom'" class="mt-4 grid gap-5 lg:grid-cols-2 lg:items-start">
          <ColorField
            :model-value="form.primary_color || '#FF007F'"
            label="Màu chính"
            @update:model-value="form.primary_color = $event"
          />
          <ColorField
            :model-value="form.text_color || '#111111'"
            label="Màu chữ"
            @update:model-value="form.text_color = $event"
          />
          <div>
            <label class="mb-2 block text-sm text-slate-300">Chế độ giao diện</label>
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
            <label class="mb-2 block text-sm text-slate-300">Kiểu nền</label>
            <select v-model="form.bg_type" class="field">
              <option v-for="option in bgTypeOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="mb-2 block text-sm text-slate-300">Kiểu avatar</label>
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
            <label class="mb-2 block text-sm text-slate-300">Kiểu nút</label>
            <select v-model="form.button_style" class="field">
              <option v-for="option in buttonStyleOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
        </div>
      </section>

      <section v-show="activeTab === 'content'" class="glass-panel page-panel rounded-[2rem]">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p class="profile-form-section__title !mb-1">Nội dung trang công khai</p>
            <p class="text-sm text-slate-400">Chia thành từng mục — giới thiệu, thư viện ảnh, QR, form đặt lịch.</p>
          </div>
          <button class="btn-secondary text-sm" type="button" @click="fillDemoContent">
            Điền mẫu
          </button>
        </div>
        <div class="mt-5">
          <ProfileLayoutBuilder v-model="layoutModel" mode="content" />
        </div>
      </section>

      <section v-show="activeTab === 'preview'" class="glass-panel page-panel overflow-hidden rounded-[2rem]">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <p class="profile-form-section__title !mb-1">Xem trước trực tiếp</p>
            <p class="text-sm text-slate-400">Đây là trang công khai khách hàng sẽ thấy.</p>
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
