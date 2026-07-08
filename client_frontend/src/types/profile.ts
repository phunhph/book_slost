export type BlockType =
  | 'hero'
  | 'social_links'
  | 'gallery'
  | 'qr_codes'
  | 'about'
  | 'booking'
  | 'contact'

export type SocialPlatform =
  | 'instagram'
  | 'tiktok'
  | 'facebook'
  | 'youtube'
  | 'twitter'
  | 'website'
  | 'shopee'
  | 'zalo'
  | 'other'

export interface SocialLinkItem {
  platform: SocialPlatform | string
  label?: string | null
  url: string
}

export interface GalleryItem {
  url: string
  alt?: string | null
  caption?: string | null
}

export interface QrCodeItem {
  label: string
  image_url: string
  target_url?: string | null
}

export interface ProfileBlock {
  id: string
  type: BlockType
  active: boolean
  order: number
  data: Record<string, unknown>
}

export interface ProfileLayoutV2 {
  version: 2
  blocks: ProfileBlock[]
}

export interface UserProfile {
  user_id: string
  username: string | null
  display_name: string | null
  bio: string | null
  avatar_url: string | null
  theme_mode: 'light' | 'dark' | 'custom'
  font_family: string
  primary_color: string
  text_color: string
  bg_type: 'color' | 'gradient' | 'image'
  bg_value: string | null
  avatar_style: 'circle' | 'square' | 'rounded'
  button_style: 'filled' | 'outline' | 'shadow'
  phone: string | null
  zalo: string | null
  messenger: string | null
  pricing_type: 'match' | 'hourly'
  price_per_match: number
  price_per_hour: number
  currency: string
  bank_name?: string | null
  bank_code?: string | null
  bank_account_number?: string | null
  bank_account_name?: string | null
  layout_structure: ProfileLayoutV2 | Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface KolPublicCard {
  user_id: string
  username: string | null
  display_name: string | null
  bio: string | null
  avatar_url: string | null
  primary_color: string | null
  pricing_type?: string | null
  price_per_match?: number | null
  price_per_hour?: number | null
  currency?: string | null
  has_bank_account?: boolean
}
