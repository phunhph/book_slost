import type { ProfileLayoutV2 } from '@/types/profile'

const GALLERY_IMAGES = [
  {
    url: 'https://images.unsplash.com/photo-1611162617474-5b21e039e566?auto=format&fit=crop&w=900&q=80',
    alt: 'Social content',
    caption: 'Reels & short-form storytelling',
  },
  {
    url: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80',
    alt: 'Product showcase',
    caption: 'Product unboxing & review',
  },
  {
    url: 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=900&q=80',
    alt: 'Brand collaboration',
    caption: 'On-site brand activation',
  },
  {
    url: 'https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?auto=format&fit=crop&w=900&q=80',
    alt: 'Lifestyle shoot',
    caption: 'Lifestyle & travel content',
  },
]

const SOCIAL_ITEMS = [
  { platform: 'instagram', label: 'Instagram', url: 'https://instagram.com/creator.demo' },
  { platform: 'tiktok', label: 'TikTok', url: 'https://tiktok.com/@creatordemo' },
  { platform: 'youtube', label: 'YouTube', url: 'https://youtube.com/@creatordemo' },
  { platform: 'website', label: 'Website', url: 'https://slost.app' },
]

const QR_ITEMS = [
  {
    label: 'Zalo QR',
    image_url: 'https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=zalo://creator-demo',
    target_url: 'https://zalo.me/creator-demo',
  },
  {
    label: 'Booking QR',
    image_url: 'https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=https://slost.app/kol/creator-demo',
    target_url: 'https://slost.app/kol/creator-demo',
  },
]

export const DEMO_PROFILE_COPY = {
  bio: 'KOL lifestyle & tech | Sẵn sàng hợp tác thương hiệu FMCG, beauty, fintech.',
  about:
    '<p>Xin chào, mình là <strong>Creator Demo</strong> — KOL chuyên lifestyle, review sản phẩm và storytelling ngắn.</p>' +
    '<ul><li>120K+ followers trên TikTok &amp; Instagram</li><li>Tỷ lệ engagement trung bình <strong>6.8%</strong></li><li>Đã hợp tác với 30+ thương hiệu trong nước</li></ul>' +
    '<p>Mình nhận booking review, livestream, UGC và chiến dịch dài hạn. Hãy để lại brief qua form bên dưới nhé!</p>',
  phone: '0901000001',
  zalo: 'creator-demo',
  messenger: 'creator.demo',
}

export function buildDemoLayoutV2(contact = DEMO_PROFILE_COPY): ProfileLayoutV2 {
  return {
    version: 2,
    blocks: [
      { id: 'hero', type: 'hero', active: true, order: 0, data: {} },
      {
        id: 'about-demo',
        type: 'about',
        active: true,
        order: 1,
        data: { content: contact.about },
      },
      {
        id: 'social-demo',
        type: 'social_links',
        active: true,
        order: 2,
        data: { items: SOCIAL_ITEMS },
      },
      {
        id: 'gallery-demo',
        type: 'gallery',
        active: true,
        order: 3,
        data: { layout: 'grid', items: GALLERY_IMAGES },
      },
      {
        id: 'qr-demo',
        type: 'qr_codes',
        active: true,
        order: 4,
        data: { items: QR_ITEMS },
      },
      {
        id: 'contact-demo',
        type: 'contact',
        active: true,
        order: 5,
        data: {
          phone: contact.phone,
          zalo: contact.zalo,
          messenger: contact.messenger,
        },
      },
      {
        id: 'booking',
        type: 'booking',
        active: true,
        order: 6,
        data: {
          title: 'Đặt lịch hợp tác',
          subtitle: 'Gửi brief, ngân sách dự kiến và timeline để mình phản hồi trong 24h.',
        },
      },
    ],
  }
}

export const DEMO_AVATAR_URL =
  'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=600&q=80'

export const DEMO_THEME = {
  text_color: '#0F172A',
  primary_color: '#DB2777',
  bg_type: 'gradient',
  bg_value: 'linear-gradient(135deg, #FDF2F8 0%, #E0F2FE 100%)',
}
