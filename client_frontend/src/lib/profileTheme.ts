import type { UserProfile } from '@/types/profile'

export const DEFAULT_PROFILE_GRADIENT =
  'linear-gradient(135deg, rgba(139,92,246,0.75), rgba(217,70,239,0.65))'
export const DEFAULT_PROFILE_SOLID = '#0f172a'

interface GradientPreset {
  label: string
  value: string
  textColor: string
  primaryColor: string
}

const GRADIENT_PRESETS: GradientPreset[] = [
  {
    label: 'Pink sky',
    value: 'linear-gradient(135deg, #FDF2F8 0%, #E0F2FE 100%)',
    textColor: '#0F172A',
    primaryColor: '#DB2777',
  },
  {
    label: 'Violet pulse',
    value: 'linear-gradient(135deg, #8B5CF6 0%, #D946EF 100%)',
    textColor: '#FFFFFF',
    primaryColor: '#F9A8D4',
  },
  {
    label: 'Ocean',
    value: 'linear-gradient(135deg, #0F172A 0%, #1D4ED8 100%)',
    textColor: '#F8FAFC',
    primaryColor: '#38BDF8',
  },
  {
    label: 'Sunset',
    value: 'linear-gradient(135deg, #F59E0B 0%, #EF4444 100%)',
    textColor: '#111827',
    primaryColor: '#7C2D12',
  },
  {
    label: 'Mint',
    value: 'linear-gradient(135deg, #ECFDF5 0%, #06B6D4 100%)',
    textColor: '#0F172A',
    primaryColor: '#0D9488',
  },
  {
    label: 'Dark glow',
    value: 'linear-gradient(135deg, #111827 0%, #4C1D95 100%)',
    textColor: '#F8FAFC',
    primaryColor: '#C084FC',
  },
]

function normalizeHex(value: string | null | undefined): string | null {
  if (!value) return null
  const trimmed = value.trim()
  const short = /^#([0-9a-fA-F]{3})$/.exec(trimmed)
  if (short) {
    const [r, g, b] = short[1]
    return `#${r}${r}${g}${g}${b}${b}`.toUpperCase()
  }
  const full = /^#([0-9a-fA-F]{6})$/.exec(trimmed)
  if (full) {
    return `#${full[1].toUpperCase()}`
  }
  return null
}

function normalizeGradientValue(value: string | null | undefined): string {
  if (!value) return ''
  return value.replace(/\s+/g, ' ').trim().toLowerCase()
}

function parseLinearGradient(value: string | null | undefined) {
  if (!value) return null
  const match = value.match(
    /linear-gradient\(\s*(\d+)deg\s*,\s*(#[0-9a-fA-F]{3,6}|rgba?\([^)]+\)|[a-z]+)\s*0%\s*,\s*(#[0-9a-fA-F]{3,6}|rgba?\([^)]+\)|[a-z]+)\s*100%\s*\)/i,
  )
  if (!match) return null
  return {
    angle: Number(match[1]),
    start: normalizeHex(match[2]) ?? match[2],
    end: normalizeHex(match[3]) ?? match[3],
  }
}

function channelLuminance(hex: string): number {
  const normalized = normalizeHex(hex)
  if (!normalized) return 0
  const channels = [normalized.slice(1, 3), normalized.slice(3, 5), normalized.slice(5, 7)].map((part) => {
    const channel = parseInt(part, 16) / 255
    return channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4
  })
  return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
}

function suggestTextColorForGradient(start: string, end: string): string {
  const average = (channelLuminance(start) + channelLuminance(end)) / 2
  return average > 0.52 ? '#0F172A' : '#F8FAFC'
}

function suggestPrimaryForGradient(start: string, end: string): string {
  const startHex = normalizeHex(start)
  const endHex = normalizeHex(end)
  if (!startHex || !endHex) return '#8B5CF6'
  return channelLuminance(startHex) <= channelLuminance(endHex) ? startHex : endHex
}

function findGradientPreset(bgValue: string | null | undefined): GradientPreset | null {
  const normalized = normalizeGradientValue(bgValue)
  return GRADIENT_PRESETS.find((preset) => normalizeGradientValue(preset.value) === normalized) ?? null
}

function resolveThemeForBackground(
  bgType: string | null | undefined,
  bgValue: string | null | undefined,
): { textColor: string; primaryColor: string } | null {
  if (bgType !== 'gradient' || !bgValue) return null

  const preset = findGradientPreset(bgValue)
  if (preset) {
    return { textColor: preset.textColor, primaryColor: preset.primaryColor }
  }

  const parsed = parseLinearGradient(bgValue)
  if (!parsed) return null

  return {
    textColor: suggestTextColorForGradient(parsed.start, parsed.end),
    primaryColor: suggestPrimaryForGradient(parsed.start, parsed.end),
  }
}

export function withResolvedProfileTheme<T extends UserProfile>(profile: T): T {
  const theme = resolveThemeForBackground(profile.bg_type, profile.bg_value)
  if (!theme || profile.bg_type !== 'gradient') return profile

  return {
    ...profile,
    text_color: theme.textColor,
    primary_color: theme.primaryColor,
  }
}

export function getRelativeLuminance(hex: string): number {
  return channelLuminance(hex)
}

export function isDarkColor(color: string | null | undefined): boolean {
  const normalized = normalizeHex(color)
  if (!normalized) return true
  return getRelativeLuminance(normalized) < 0.45
}

export function isGradientDark(gradient: string): boolean {
  const hexMatches = gradient.match(/#[0-9a-fA-F]{3,8}/g)
  if (!hexMatches || hexMatches.length === 0) {
    const lower = gradient.toLowerCase()
    return !lower.includes('white') && !lower.includes('light') && !lower.includes('transparent')
  }

  let darkCount = 0
  for (const hex of hexMatches) {
    if (isDarkColor(hex)) {
      darkCount++
    }
  }

  return darkCount >= hexMatches.length / 2
}

export function contrastTextOn(color: string | null | undefined): string {
  return isDarkColor(color) ? '#FFFFFF' : '#111827'
}

export function profileAccentVars(primaryColor: string | null | undefined) {
  const accent = normalizeHex(primaryColor) ?? '#8B5CF6'
  return {
    '--profile-accent': accent,
    '--profile-accent-soft': `${accent}22`,
    '--profile-accent-border': `${accent}55`,
    '--profile-button-text': contrastTextOn(accent),
  } as Record<string, string>
}

export function buildProfileSurfaceStyle(
  profile: Pick<UserProfile, 'bg_type' | 'bg_value' | 'text_color' | 'font_family' | 'primary_color'>,
) {
  const resolved = withResolvedProfileTheme(profile as UserProfile)
  const style: Record<string, string> = {}

  let isBgDark = true
  if (resolved.bg_type === 'image' && resolved.bg_value) {
    style.backgroundImage = `linear-gradient(180deg, rgba(2, 6, 23, 0.44), rgba(2, 6, 23, 0.88)), url(${resolved.bg_value})`
    style.backgroundSize = 'cover'
    style.backgroundPosition = 'center'
    isBgDark = true
  } else if (resolved.bg_type === 'gradient') {
    const val = resolved.bg_value || DEFAULT_PROFILE_GRADIENT
    style.background = val
    isBgDark = isGradientDark(val)
  } else {
    const solidColor = resolved.bg_value || DEFAULT_PROFILE_SOLID
    style.background = solidColor
    isBgDark = isDarkColor(solidColor)
  }

  let textColor = resolved.text_color || (isBgDark ? '#F8FAFC' : '#111827')
  const isTextDark = isDarkColor(textColor)

  if (isBgDark === isTextDark) {
    textColor = isBgDark ? '#F8FAFC' : '#111827'
  }

  style.color = textColor

  if (resolved.font_family) {
    style.fontFamily = resolved.font_family
  }

  return style
}
