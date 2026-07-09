import { normalizeHex, resolveThemeForBackground } from './colorUtils'

export interface ProfileThemeInput {
  bg_type?: string | null
  bg_value?: string | null
  text_color?: string | null
  primary_color?: string | null
  font_family?: string | null
  theme_mode?: string | null
}

export const DEFAULT_PROFILE_GRADIENT =
  'linear-gradient(135deg, rgba(139,92,246,0.75), rgba(217,70,239,0.65))'
export const DEFAULT_PROFILE_SOLID = '#0f172a'

export function withResolvedProfileTheme<T extends ProfileThemeInput>(profile: T): T {
  const theme = resolveThemeForBackground(profile.bg_type, profile.bg_value)
  if (!theme || profile.bg_type !== 'gradient') return profile

  return {
    ...profile,
    text_color: theme.textColor,
    primary_color: theme.primaryColor,
  }
}

export function buildProfileSurfaceStyle(profile: ProfileThemeInput): Record<string, string> {
  const resolved = withResolvedProfileTheme(profile)
  const style: Record<string, string> = {}

  if (resolved.bg_type === 'image' && resolved.bg_value) {
    style.backgroundImage = `linear-gradient(180deg, rgba(2, 6, 23, 0.44), rgba(2, 6, 23, 0.88)), url(${resolved.bg_value})`
    style.backgroundSize = 'cover'
    style.backgroundPosition = 'center'
  } else if (resolved.bg_type === 'gradient') {
    style.background = resolved.bg_value || DEFAULT_PROFILE_GRADIENT
  } else {
    style.background = resolved.bg_value || DEFAULT_PROFILE_SOLID
  }

  style.color = resolved.text_color || '#F8FAFC'

  if (resolved.font_family) {
    style.fontFamily = resolved.font_family
  }

  return style
}

export const PROFILE_BLOCK_IDS = [
  'media_block',
  'booking_block',
  'products_block',
  'affiliate_block',
] as const

export type ProfileBlockId = (typeof PROFILE_BLOCK_IDS)[number]

export interface LayoutBlock {
  id: string
  active: boolean
}

export function normalizeLayoutStructure(blocks: unknown): LayoutBlock[] {
  if (blocks && typeof blocks === 'object' && !Array.isArray(blocks) && (blocks as { version?: number }).version === 2) {
    const v2Blocks = (blocks as { blocks?: Array<{ id: string; active: boolean }> }).blocks
    return Array.isArray(v2Blocks)
      ? v2Blocks.map((block) => ({ id: block.id, active: block.active }))
      : []
  }

  const list = Array.isArray(blocks) ? blocks : []
  const byId = new Map(list.map((block) => [block.id, block.active]))
  return PROFILE_BLOCK_IDS.map((id) => ({
    id,
    active: byId.get(id) ?? false,
  }))
}

export function publicProfilePath(username: string) {
  return `/kol/${encodeURIComponent(username)}`
}

function channelHex(value: string | null | undefined): string | null {
  return normalizeHex(value)
}

export function getRelativeLuminance(hex: string): number {
  const normalized = channelHex(hex)
  if (!normalized) return 0

  const channels = [normalized.slice(1, 3), normalized.slice(3, 5), normalized.slice(5, 7)].map((part) => {
    const channel = parseInt(part, 16) / 255
    return channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4
  })

  return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
}

export function isDarkColor(color: string | null | undefined): boolean {
  const normalized = channelHex(color)
  if (!normalized) return true
  return getRelativeLuminance(normalized) < 0.45
}

export function contrastTextOn(color: string | null | undefined): string {
  return isDarkColor(color) ? '#FFFFFF' : '#111827'
}

export function profileAccentVars(primaryColor: string | null | undefined) {
  const accent = channelHex(primaryColor) ?? '#8B5CF6'
  return {
    '--profile-accent': accent,
    '--profile-accent-soft': `${accent}22`,
    '--profile-accent-border': `${accent}55`,
    '--profile-button-text': contrastTextOn(accent),
  } as Record<string, string>
}
