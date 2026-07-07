# INSTRUCTIONS: FRONTEND PHASE 1 - AUTH & CUSTOM PROFILE LAYOUT
## Hệ thống Affiliate & Booking Core System (2 dự án Next.js + Tailwind CSS)

Tài liệu này định nghĩa cấu trúc thư mục, quy chuẩn UI/UX và nguyên tắc kết nối API cho hệ thống frontend. Ở phase 1, frontend phải được tách thành 2 project độc lập: một project admin và một project client/public.

---

## 1. Tech Stack và cấu hình
- **Framework:** Next.js 14+ với App Router.
- **Language:** TypeScript bật strict mode.
- **Styling:** Tailwind CSS.
- **State management:** ưu tiên React Context hoặc Zustand cho state UI của dashboard/profile editor.
- **Drag and drop:** ưu tiên `@dnd-kit/core`; chỉ dùng thư viện khác nếu có lý do rõ ràng.
- **HTTP client:** ưu tiên native `fetch`; có thể dùng Axios nếu toàn dự án đã thống nhất.

### Nguyên tắc render
- Trang public profile ưu tiên **Server Components** để giữ SEO và tối ưu tải trang.
- Các thành phần có tương tác mạnh như kéo thả, color picker, form editor phải tách thành **Client Components** với `'use client'`.
- Tách phần hiển thị và phần gọi API rõ ràng để dễ mở rộng sang phase Products và Booking.

---

## 2. Biến môi trường
Tạo file `.env.local` cho từng project frontend.

```env
# admin_frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id_here.apps.googleusercontent.com
NEXT_PUBLIC_ENV=development
NEXT_PUBLIC_CLIENT_APP_URL=http://localhost:3001
```

```env
# client_frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_ENV=development
```

### Quy ước
- Chỉ expose các biến thực sự cần cho client bằng tiền tố `NEXT_PUBLIC_`.
- Không hard-code API URL trong component hoặc service.

---

## 3. Kiến trúc thư mục theo mô-đun
Frontend nên được tổ chức theo mô hình feature-based để các phase sau có thể mở rộng mà không phá vỡ cấu trúc cũ.

```text
admin_frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── login/page.tsx
│   ├── register/page.tsx
│   ├── dashboard/page.tsx
│   └── edit-profile/page.tsx
├── components/ui/
├── features/auth/
│   ├── components/
│   └── services/
├── features/profile/
│   ├── components/
│   ├── services/
│   └── types/
├── .env.local
├── tailwind.config.ts
└── tsconfig.json
```

```text
client_frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── [username]/page.tsx
├── components/ui/
├── features/profile/
│   ├── components/
│   ├── services/
│   └── types/
├── .env.local
├── tailwind.config.ts
└── tsconfig.json
```

### Quy tắc tổ chức mã
- `components/ui` chỉ chứa component dùng chung, không nhúng business logic.
- Mỗi feature tự quản lý `components`, `services`, `hooks`, `types` của riêng nó.
- Kiểu dữ liệu API response/request phải khai báo rõ trong `types` hoặc `schemas` phía frontend.

---

## 4. Quy chuẩn render UI động và customization
### 4.1. Dynamic layout mapping
Tại `client_frontend/app/[username]/page.tsx`, frontend phải fetch dữ liệu profile từ backend và render block theo `layout_structure`.

```tsx
layoutStructure.map((block) => {
  if (!block.active) return null;

  switch (block.id) {
    case "media_block":
      return <MediaBlock key={block.id} />;
    case "booking_block":
      return <BookingBlock key={block.id} />;
    case "products_block":
      return <ProductsBlock key={block.id} />;
    case "affiliate_block":
      return <AffiliateBlock key={block.id} />;
    default:
      return null;
  }
});
```

### 4.2. Dynamic styling
Frontend phải áp dụng cấu hình styling từ API bằng inline style hoặc CSS variables.

- **Background:** hỗ trợ `bg_type` gồm `color`, `gradient`, `image`.
- **Buttons:** dùng `primary_color` và `button_style` để xác định màu, border, shadow, độ bo góc.
- **Typography:** gán `font_family` ở wrapper cấp cao để đồng bộ toàn trang.
- **Avatar:** dùng `avatar_style` để map sang các class hiển thị phù hợp.

### 4.3. Trạng thái tải dữ liệu
- Luôn có loading state hoặc skeleton cho public profile trong `client_frontend` và trang edit profile trong `admin_frontend`.
- Có empty state rõ ràng khi chưa có dữ liệu profile hoặc block bị tắt toàn bộ.
- Có fallback an toàn nếu backend trả block không hợp lệ.

---

## 5. Nguyên tắc code dành cho Cursor AI
- Luôn viết code sạch, có type/interface đầy đủ cho profile data và layout block.
- Không để logic API nằm rải rác trong page nếu có thể tách vào `services`.
- Tách component lớn thành các phần nhỏ, dễ test và dễ tái sử dụng.
- Ưu tiên tên biến, tên component, tên service nhất quán với domain: `profile`, `auth`, `booking`, `affiliate`.
- Nếu cần thêm dependency mới, chọn dependency đang còn được duy trì và phù hợp với App Router.

---

## 6. Tiêu chí hoàn thành phase 1
- Có luồng đăng ký/đăng nhập cơ bản.
- Có 2 project tách biệt: `admin_frontend` và `client_frontend`.
- Có dashboard hoặc màn hình edit profile cho admin.
- Có public profile route theo `[username]` trong `client_frontend`.
- Có render động theo `layout_structure`.
- Có áp dụng được màu sắc, nền, font và style nút từ dữ liệu backend.
