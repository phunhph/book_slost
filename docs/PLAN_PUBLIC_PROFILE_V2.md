# Plan: Public Profile V2 — Trang KOL tự do, không bị nhét trong ô nhỏ

> **Ngày:** 2026-07-08  
> **Trạng thái:** Đề xuất — chưa implement  
> **Liên quan:** `kol_frontend` (editor), `client_frontend` (public `/kol/:username`), `backend` (`user_profiles.layout_structure`)

---

## 1. Vấn đề hiện tại

### 1.1 Trải nghiệm người xem (client)
- Profile bị **nhốt trong khung nhỏ** (hero card tối + các `theme-card` bên cạnh) → cảm giác chật, không giống landing page creator thật.
- Nội dung **hardcode** trong từng block (`media_block`, `products_block`…) — KOL không tự viết được.
- **Meta UI lộ ra** trên trang public: "Primary color", "Theme mode", "4 active blocks" — đây là thông tin debug, không phải nội dung cho khách.
- Layout **2 cột cố định** (trái profile + stats, phải blocks) — không responsive theo ý KOL.
- Contact chỉ có Phone / Zalo / Messenger — **thiếu** QR, Instagram, TikTok, YouTube, link portfolio, gallery ảnh.

### 1.2 Trải nghiệm KOL (workspace)
- Editor chỉ bật/tắt 4 block cố định — **không sửa nội dung** từng block.
- Preview nhỏ, không phản ánh đúng layout full-page.
- Không có khái niệm **"thêm block → có data mới hiện"** — chỉ toggle on/off.

### 1.3 Hạn chế kỹ thuật
```json
// layout_structure hiện tại — quá mỏng
{ "id": "media_block", "active": true }
```
- Chỉ lưu `id` + `active`, không lưu **payload** (ảnh, link, text, QR).
- `ALLOWED_BLOCK_IDS` cố định 4 id — khó mở rộng.
- Contact fields rời (`phone`, `zalo`, `messenger`) không gom với social/QR.

---

## 2. Mục tiêu (Product)

| # | Mục tiêu |
|---|----------|
| G1 | Trang public **full-width, full-page** — cảm giác "link in bio / creator landing", không phải widget trong admin. |
| G2 | KOL **tự thêm/bớt/sắp xếp** section; section nào **không có dữ liệu thì không render** (không hiện ô trống). |
| G3 | Hỗ trợ **gallery ảnh**, **QR** (Zalo/booking/affiliate), **mạng xã hội** (Instagram, TikTok, Facebook, YouTube, website…). |
| G4 | Editor trực quan: kéo thả thứ tự, preview **1:1** với trang public. |
| G5 | Tương thích ngược: profile cũ vẫn hiển thị được sau migration. |

---

## 3. Định hướng UX — Layout mới

### 3.1 Cấu trúc trang public (đề xuất)

```
┌─────────────────────────────────────────────────────────────┐
│  HERO (full bleed background — gradient/ảnh toàn trang)      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Avatar lớn │ Tên │ @username │ Bio                    │    │
│  │ [CTA Book] [CTA Social primary]                        │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  SECTION: Social links (icon row / pill buttons) — optional  │
├─────────────────────────────────────────────────────────────┤
│  SECTION: Gallery (grid 2–4 cột, lightbox) — optional        │
├─────────────────────────────────────────────────────────────┤
│  SECTION: QR codes (1–3 card: Zalo, Booking, Payment…)       │
├─────────────────────────────────────────────────────────────┤
│  SECTION: Rich text / About — optional                       │
├─────────────────────────────────────────────────────────────┤
│  SECTION: Booking form (full width, không nested card)       │
├─────────────────────────────────────────────────────────────┤
│  SECTION: Products / Affiliate — optional (phase sau)        │
└─────────────────────────────────────────────────────────────┘
```

**Nguyên tắc:**
- **Một lớp nền** cho cả trang (`bg_type` / `bg_value`), không bọc thêm `glass-panel` lồng nhau.
- **Không hiển thị** "Primary color / Theme mode / Layout blocks" trên public.
- Section render theo **thứ tự trong `layout_structure`**.
- Section **ẩn hoàn toàn** nếu: `active: false` HOẶC payload rỗng (rule từng loại block).

### 3.2 Editor KOL (workspace `/profile`)

Chia **2 panel** (desktop):
- **Trái:** Live preview full-page (iframe hoặc component scale) — scroll độc lập.
- **Phải:** "Page builder" — danh sách section có thể kéo thả (`@dnd-kit`).

Mỗi section trong builder:
- Toggle hiển thị
- Form nội dung riêng (upload URL ảnh, paste link social, upload/generate QR)
- Nút "Thêm section" → chọn loại từ thư viện

**Thư viện section (MVP):**

| Type | Mô tả | Điều kiện hiện |
|------|--------|----------------|
| `hero` | Luôn có (gắn display_name, bio, avatar) | Luôn hiện |
| `social_links` | Danh sách link + icon | ≥ 1 link hợp lệ |
| `gallery` | Mảng `{ url, caption? }` | ≥ 1 ảnh |
| `qr_codes` | Mảng `{ label, image_url hoặc payload }` | ≥ 1 QR |
| `about` | Markdown / rich text ngắn | Có nội dung |
| `booking` | Form đặt lịch | `active: true` (mặc định bật) |
| `contact` | Phone, Zalo, Messenger (legacy) | ≥ 1 field |
| `custom_html` | (Optional, phase 2) Text tự do | Có content |

---

## 4. Data model V2

### 4.1 Thay `layout_structure` mỏng → block có payload

```typescript
// types/profile-blocks.ts (shared concept)

type BlockBase = {
  id: string           // uuid client-generated, stable khi reorder
  type: BlockType
  active: boolean
  order: number
}

type HeroBlock = BlockBase & {
  type: 'hero'
  // override optional; fallback profile fields
  data?: {
    headline?: string
    subheadline?: string
    cta_label?: string
  }
}

type SocialLinksBlock = BlockBase & {
  type: 'social_links'
  data: {
    items: Array<{
      platform: 'instagram' | 'tiktok' | 'facebook' | 'youtube' | 'twitter' | 'website' | 'shopee' | 'other'
      label?: string
      url: string
    }>
  }
}

type GalleryBlock = BlockBase & {
  type: 'gallery'
  data: {
    layout: 'grid' | 'carousel'
    items: Array<{ url: string; alt?: string; caption?: string }>
  }
}

type QrCodesBlock = BlockBase & {
  type: 'qr_codes'
  data: {
    items: Array<{
      label: string           // "Zalo", "Book me", "Affiliate"
      image_url: string       // upload hoặc generate server-side
      target_url?: string     // optional deeplink
    }>
  }
}

type AboutBlock = BlockBase & {
  type: 'about'
  data: { content: string }
}

type BookingBlock = BlockBase & {
  type: 'booking'
  data?: { title?: string; subtitle?: string }
}

type ContactBlock = BlockBase & {
  type: 'contact'
  data: {
    phone?: string
    zalo?: string
    messenger?: string
  }
}
```

Lưu trong PostgreSQL: **một cột JSONB** `layout_structure` (giữ tên cột, đổi shape) hoặc thêm `profile_blocks JSONB` mới + deprecate dần.

**Khuyến nghị:** Giữ `layout_structure`, bump schema version:

```json
{
  "version": 2,
  "blocks": [ /* ... */ ]
}
```

### 4.2 Profile scalar fields (giữ / gom)

| Field | Xử lý |
|-------|--------|
| `display_name`, `username`, `bio`, `avatar_url` | Giữ — dùng cho hero mặc định |
| `primary_color`, `text_color`, `bg_*`, `font_*` | Giữ — theme toàn trang |
| `phone`, `zalo`, `messenger` | Migration → `contact` block hoặc hero; giữ backward compat đọc cũ |
| `theme_mode` | Giữ; có thể auto-contrast (đã có một phần) |

### 4.3 Validation backend

- Pydantic discriminated union theo `type`.
- URL validate cho social/gallery.
- Giới hạn: gallery ≤ 12 ảnh, social ≤ 10 link, QR ≤ 5 (configurable).
- Sanitize `about.content` (no script).

---

## 5. API changes

| Endpoint | Thay đổi |
|----------|----------|
| `GET /api/profiles/public/{username}` | Trả `layout_structure` v2; server có thể **strip** block rỗng trước khi trả (optional). |
| `PUT /api/profiles/by-user/{id}` | Nhận schema v2; auth KOL only (đã có). |
| `POST /api/profiles/upload` (mới) | Upload ảnh/QR → S3/local storage → trả URL. Phase 1 có thể chỉ paste URL. |
| `POST /api/profiles/qr` (mới, optional) | Generate QR từ `target_url` → trả `image_url`. |

**Migration endpoint (internal):** script Alembic hoặc one-off transform v1 → v2.

---

## 6. Frontend implementation map

### 6.1 `client_frontend` — Public page rewrite

| File / module | Việc cần làm |
|---------------|--------------|
| `views/KolDetailView.vue` | **Xóa** layout 2 cột + stats cards; thay bằng `ProfilePageRenderer`. |
| `components/profile/blocks/*` | Một component / block type: `HeroBlock.vue`, `SocialLinksBlock.vue`, … |
| `components/profile/ProfilePageRenderer.vue` | Loop `blocks`, filter visible, sort by `order`. |
| `lib/profileTheme.ts` | Theme áp dụng lên `<main>` full page, không lồng card. |
| `lib/profileBlocks.ts` | `isBlockVisible(block, profile)`, `migrateV1ToV2(profile)`. |

### 6.2 `kol_frontend` — Page builder

| File / module | Việc cần làm |
|---------------|--------------|
| `views/ProfileView.vue` | Thay form dài + preview nhỏ → **Page builder** layout. |
| `components/profile-builder/BlockList.vue` | Drag-drop reorder (`@dnd-kit/core`). |
| `components/profile-builder/editors/*` | Editor per block type. |
| `components/profile/ProfilePreviewCard.vue` | Đổi thành full-page preview hoặc embed `ProfilePageRenderer`. |

### 6.3 Shared types (khuyến nghị)

Tạo package hoặc folder copy-sync:
```
shared/profile-blocks/
  types.ts
  visibility.ts
  migrate-v1-v2.ts
```
Tránh lệch logic giữa KOL preview và client public (đã từng xung đột).

---

## 7. Migration V1 → V2

```text
V1 block id          →  V2 type(s)
─────────────────────────────────────
media_block          →  about (placeholder content) hoặc bỏ
booking_block        →  booking
products_block       →  (inactive / phase 2 products)
affiliate_block      →  (inactive / phase 2)
(phone,zalo,messenger columns) → contact block
(avatar,bio,name)    →  hero (implicit)
```

Script migration trong Alembic `20260708_xxxx_profile_blocks_v2.py`:
- Đọc mọi `user_profiles.layout_structure`
- Wrap thành `{ version: 2, blocks: [...] }`
- Map contact columns → `contact` block nếu có giá trị

---

## 8. Lộ trình triển khai (đề xuất 4 phase)

### Phase A — Quick wins (1–2 ngày)
**Mục tiêu:** Trang public đẹp hơn ngay, chưa đổi schema.

- [ ] Bỏ 3 stat cards (Primary color / Theme mode / Layout blocks) khỏi public.
- [ ] Hero full-width, bỏ `glass-panel` lồng trong `glass-panel`.
- [ ] Booking form full-width section riêng.
- [ ] Ẩn block hardcode nếu `active: false` (đã có một phần).

**Kết quả:** Hết cảm giác "ô nhỏ", chưa cần editor mới.

### Phase B — Schema V2 + social/contact (3–5 ngày)
- [ ] Backend: Pydantic v2, migration v1→v2.
- [ ] Block `social_links`, `contact`, `about` có payload.
- [ ] KOL editor: form thêm link IG/TikTok/website; reorder đơn giản (nút lên/xuống).
- [ ] Public renderer theo block type.

### Phase C — Gallery + QR (3–4 ngày)
- [ ] Block `gallery` (paste URL; sau đó upload).
- [ ] Block `qr_codes` (paste ảnh QR hoặc generate từ URL).
- [ ] Lightbox gallery trên mobile.

### Phase D — Page builder UX (5–7 ngày)
- [ ] Drag-drop `@dnd-kit`.
- [ ] Preview 1:1 full page.
- [ ] Template presets ("Minimal", "Gallery first", "Booking first").
- [ ] (Optional) `products` / `affiliate` blocks thật.

---

## 9. Wireframe logic (mobile-first)

```
Mobile:
┌──────────────┐
│    HERO      │  ← avatar center, tên, bio, CTA stack vertical
├──────────────┤
│ ○ ○ ○ ○ ○    │  ← social icons scroll ngang
├──────────────┤
│ [img][img]   │  ← gallery 2 cột
│ [img][img]   │
├──────────────┤
│ [QR] [QR]    │  ← QR scroll ngang
├──────────────┤
│ Booking form │
└──────────────┘

Desktop:
- Hero: avatar trái, text phải, max-width 960px center
- Gallery: 3–4 cột
- QR: 2–3 cột
- Booking: max-width 640px center hoặc 2 cột với about
```

---

## 10. Quy tắc "có thì hiện, không thì thôi"

| Block | `visible` khi |
|-------|----------------|
| `hero` | Luôn (fallback tên "Unnamed creator") |
| `social_links` | `active && items.length > 0` |
| `gallery` | `active && items.some(i => i.url)` |
| `qr_codes` | `active && items.length > 0` |
| `about` | `active && content.trim()` |
| `contact` | `active && (phone\|zalo\|messenger)` |
| `booking` | `active` (default true) |

**Không render:**
- Section wrapper rỗng
- Placeholder "Phone / Zalo" khi chưa điền
- Label debug / meta theme

---

## 11. Rủi ro & quyết định cần chốt

| # | Câu hỏi | Đề xuất mặc định |
|---|---------|------------------|
| Q1 | Upload ảnh hay chỉ URL? | Phase B: URL only; Phase C: upload qua API |
| Q2 | QR generate server hay KOL tự upload? | Cả hai: paste ảnh HOẶC nhập link → generate |
| Q3 | Rich text `about` — markdown hay plain? | Markdown subset (bold, link, list) |
| Q4 | Giữ 4 block cũ trong editor? | Migration sang v2, ẩn UI cũ |
| Q5 | Custom domain `/kol/:username` đủ? | Giữ; sau này thêm custom slug premium |
| Q6 | SEO | `title` / `meta description` từ `display_name` + `bio` |

---

## 12. Tiêu chí hoàn thành (Definition of Done)

- [ ] KOL mở `/profile`, thêm ≥3 loại section khác nhau, reorder, save.
- [ ] Public `/kol/:username` hiển thị **full-page**, không có stat cards debug.
- [ ] Section không có data **không xuất hiện** trên DOM.
- [ ] Preview KOL workspace **khớp** public (cùng `ProfilePageRenderer`).
- [ ] Profile seed `creator-demo` migrate v2, không vỡ booking.
- [ ] Mobile: gallery + social + booking usable trên 375px width.
- [ ] CI: backend pytest + frontend build pass.

---

## 13. File sẽ tạo/sửa (checklist dev)

```
docs/PLAN_PUBLIC_PROFILE_V2.md          ← file này
backend/app/modules/profile/
  schemas_blocks_v2.py                  ← new
  services_migrate.py                   ← new
  alembic/versions/..._profile_v2.py    ← new
client_frontend/src/
  components/profile/ProfilePageRenderer.vue
  components/profile/blocks/*.vue
  lib/profileBlocks.ts
kol_frontend/src/
  components/profile-builder/*
  views/ProfileView.vue                 ← rewrite
shared/ (optional)
  profile-blocks/types.ts
```

---

## 14. Tóm tắt cho stakeholder

> **Hiện tại** trang KOL giống dashboard demo: nhiều ô nhỏ, nội dung giả, không custom được.  
> **Hướng mới** là **creator landing page**: một trang dài, nền đẹp, section tùy chọn (ảnh, QR, mạng xã hội, booking). KOL thêm gì thì hiện đó, không thêm thì không có — không còn ô trống hay chữ debug.

**Bước tiếp theo đề xuất:** Làm **Phase A** ngay (UI public sạch, full-width) trong khi chốt schema V2, rồi **Phase B** để KOL tự thêm social + reorder.

---

*Nếu bạn đồng ý hướng này, bước implement tiếp theo nên là Phase A (không đổi DB) hoặc Phase B (đổi DB + editor) tùy mức độ custom bạn cần gấp.*
