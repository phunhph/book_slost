import type { BlockType, ProfileBlock, ProfileLayoutV2, UserProfile } from '@/types/profile'

function newId() {
  return crypto.randomUUID()
}

function defaultData(type: BlockType): Record<string, unknown> {
  switch (type) {
    case 'social_links':
      return { items: [] }
    case 'gallery':
      return { layout: 'grid', items: [] }
    case 'qr_codes':
      return { items: [] }
    case 'about':
      return { content: '' }
    case 'contact':
      return { phone: null, zalo: null, messenger: null }
    case 'booking':
      return {
        title: 'Request a campaign',
        subtitle: 'Share your campaign goals and preferred schedule.',
      }
    default:
      return {}
  }
}

export function defaultLayoutV2(profile?: Partial<UserProfile>): ProfileLayoutV2 {
  const blocks: ProfileBlock[] = []
  let order = 0

  blocks.push({ id: 'hero', type: 'hero', active: true, order: order++, data: {} })

  if (profile?.bio?.trim()) {
    blocks.push({
      id: newId(),
      type: 'about',
      active: true,
      order: order++,
      data: { content: profile.bio.trim() },
    })
  }

  if (profile?.phone || profile?.zalo || profile?.messenger) {
    blocks.push({
      id: newId(),
      type: 'contact',
      active: true,
      order: order++,
      data: { phone: profile.phone, zalo: profile.zalo, messenger: profile.messenger },
    })
  }

  blocks.push({ id: 'booking', type: 'booking', active: true, order: order++, data: defaultData('booking') })

  for (const type of ['social_links', 'gallery', 'qr_codes'] as BlockType[]) {
    blocks.push({ id: newId(), type, active: false, order: order++, data: defaultData(type) })
  }

  return { version: 2, blocks }
}

export function migrateLayoutToV2(raw: unknown, profile?: Partial<UserProfile>): ProfileLayoutV2 {
  if (raw && typeof raw === 'object' && !Array.isArray(raw) && (raw as ProfileLayoutV2).version === 2) {
    return normalizeLayoutV2(raw as ProfileLayoutV2)
  }

  const v1 = Array.isArray(raw) ? raw : []
  const v1Map = Object.fromEntries(
    v1.filter((item) => item && typeof item === 'object').map((item) => [(item as ProfileBlock).id, (item as ProfileBlock).active]),
  )

  return defaultLayoutV2({
    bio: v1Map.media_block !== false ? profile?.bio : undefined,
    phone: profile?.phone,
    zalo: profile?.zalo,
    messenger: profile?.messenger,
  })
}

export function normalizeLayoutV2(raw: ProfileLayoutV2 | unknown): ProfileLayoutV2 {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
    return defaultLayoutV2()
  }

  const candidate = raw as ProfileLayoutV2
  const blockList = Array.isArray(candidate.blocks) ? candidate.blocks : []

  const sorted = [...blockList].sort((a, b) => a.order - b.order)
  const blocks = sorted.map((block, index) => ({
    ...block,
    id: block.id || newId(),
    order: index,
    data: block.data ?? defaultData(block.type),
  }))

  if (!blocks.some((block) => block.type === 'hero')) {
    blocks.unshift({ id: 'hero', type: 'hero', active: true, order: 0, data: {} })
  }
  if (!blocks.some((block) => block.type === 'booking')) {
    blocks.push({ id: 'booking', type: 'booking', active: true, order: blocks.length, data: defaultData('booking') })
  }

  return {
    version: 2,
    blocks: blocks.map((block, index) => ({ ...block, order: index })),
  }
}

export function parseLayout(profile: UserProfile): ProfileLayoutV2 {
  return migrateLayoutToV2(profile.layout_structure, profile)
}

export function getContactData(block: ProfileBlock, profile: UserProfile) {
  const data = block.data as { phone?: string; zalo?: string; messenger?: string }
  return {
    phone: data.phone || profile.phone || '',
    zalo: data.zalo || profile.zalo || '',
    messenger: data.messenger || profile.messenger || '',
  }
}

export function isBlockVisible(block: ProfileBlock, profile: UserProfile): boolean {
  if (!block.active) return false

  switch (block.type) {
    case 'hero':
    case 'booking':
      return true
    case 'social_links': {
      const items = (block.data.items as Array<{ url?: string }> | undefined) ?? []
      return items.some((item) => item.url?.trim())
    }
    case 'gallery': {
      const items = (block.data.items as Array<{ url?: string }> | undefined) ?? []
      return items.some((item) => item.url?.trim())
    }
    case 'qr_codes': {
      const items = (block.data.items as Array<{ image_url?: string }> | undefined) ?? []
      return items.some((item) => item.image_url?.trim())
    }
    case 'about':
      return Boolean(String(block.data.content ?? '').trim())
    case 'contact': {
      const contact = getContactData(block, profile)
      return Boolean(contact.phone || contact.zalo || contact.messenger)
    }
    default:
      return false
  }
}

export function getVisibleBlocks(profile: UserProfile): ProfileBlock[] {
  return parseLayout(profile).blocks.filter((block) => isBlockVisible(block, profile))
}

export const BLOCK_LIBRARY: Array<{ type: BlockType; label: string; description: string }> = [
  { type: 'social_links', label: 'Social links', description: 'Instagram, TikTok, website and more.' },
  { type: 'gallery', label: 'Gallery', description: 'Showcase photos related to your brand.' },
  { type: 'qr_codes', label: 'QR codes', description: 'Zalo, booking or payment QR images.' },
  { type: 'about', label: 'About', description: 'Longer story or campaign highlights.' },
  { type: 'contact', label: 'Contact', description: 'Phone, Zalo and Messenger.' },
  { type: 'booking', label: 'Booking form', description: 'Let clients request a campaign.' },
]

export function createBlock(type: BlockType, order: number): ProfileBlock {
  return {
    id: type === 'hero' || type === 'booking' ? type : newId(),
    type,
    active: type === 'hero' || type === 'booking',
    order,
    data: defaultData(type),
  }
}

export const SOCIAL_PLATFORM_LABELS: Record<string, string> = {
  instagram: 'Instagram',
  tiktok: 'TikTok',
  facebook: 'Facebook',
  youtube: 'YouTube',
  twitter: 'X / Twitter',
  website: 'Website',
  shopee: 'Shopee',
  zalo: 'Zalo',
  other: 'Link',
}
