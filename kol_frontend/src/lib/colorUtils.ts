export function normalizeHex(value: string | null | undefined): string | null {
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

export function hexForColorInput(value: string | null | undefined, fallback = '#8B5CF6') {
  return normalizeHex(value) ?? fallback
}

export interface ParsedGradient {
  angle: number
  start: string
  end: string
}

export function parseLinearGradient(value: string | null | undefined): ParsedGradient | null {
  if (!value) return null
  const match = value.match(
    /linear-gradient\(\s*(\d+)deg\s*,\s*(#[0-9a-fA-F]{3,6}|rgba?\([^)]+\)|[a-z]+)\s*0%\s*,\s*(#[0-9a-fA-F]{3,6}|rgba?\([^)]+\)|[a-z]+)\s*100%\s*\)/i,
  )
  if (!match) return null

  const start = normalizeHex(match[2]) ?? match[2]
  const end = normalizeHex(match[3]) ?? match[3]
  return {
    angle: Number(match[1]),
    start,
    end,
  }
}

export function buildLinearGradient(angle: number, start: string, end: string) {
  const from = normalizeHex(start) ?? start
  const to = normalizeHex(end) ?? end
  return `linear-gradient(${angle}deg, ${from} 0%, ${to} 100%)`
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

export function suggestTextColorForGradient(start: string, end: string): string {
  const average = (channelLuminance(start) + channelLuminance(end)) / 2
  return average > 0.52 ? '#0F172A' : '#F8FAFC'
}

export function suggestPrimaryForGradient(start: string, end: string): string {
  const startHex = normalizeHex(start)
  const endHex = normalizeHex(end)
  if (!startHex || !endHex) return '#8B5CF6'

  const startLum = channelLuminance(startHex)
  const endLum = channelLuminance(endHex)
  return startLum <= endLum ? startHex : endHex
}

export interface GradientPreset {
  label: string
  value: string
  textColor: string
  primaryColor: string
}

export const GRADIENT_PRESETS: GradientPreset[] = [
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

export const COLOR_PRESETS = [
  '#FF007F',
  '#8B5CF6',
  '#D946EF',
  '#3B82F6',
  '#06B6D4',
  '#10B981',
  '#F59E0B',
  '#EF4444',
  '#111111',
  '#F8FAFC',
  '#FFFFFF',
  '#0F172A',
] as const

export function normalizeGradientValue(value: string | null | undefined): string {
  if (!value) return ''
  return value.replace(/\s+/g, ' ').trim().toLowerCase()
}

export function findGradientPreset(bgValue: string | null | undefined): GradientPreset | null {
  const normalized = normalizeGradientValue(bgValue)
  return GRADIENT_PRESETS.find((preset) => normalizeGradientValue(preset.value) === normalized) ?? null
}

export function resolveThemeForBackground(
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
