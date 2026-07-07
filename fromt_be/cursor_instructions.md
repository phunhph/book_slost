# INSTRUCTIONS: BACKEND PHASE 1 - AUTH & CUSTOM PROFILE
## Hệ thống Affiliate & Booking Core System (Python FastAPI + PostgreSQL)

Tài liệu này mô tả kiến trúc backend, nguyên tắc thiết kế database và coding rules cho phase 1. Dùng tài liệu này như instruction/context chính khi phát triển backend.

---

## 1. Tech Stack và điều kiện tiên quyết
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0+
- **Validation:** Pydantic v2
- **Database:** PostgreSQL 16+ với hỗ trợ `JSONB`
- **Migration:** Alembic
- **DevOps:** Docker và Docker Compose

### Nguyên tắc kỹ thuật
- Ưu tiên kiến trúc rõ ràng theo module nghiệp vụ.
- Nếu dự án dùng async engine thì code truy vấn và service phải nhất quán theo `async/await`.
- Tránh trộn router, business logic và database access trong cùng một file.

---

## 2. Kiến trúc thư mục theo chức năng
Dự án nên được tổ chức theo mô hình module-based để dễ mở rộng cho phase Products và Booking.

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # Khởi tạo app, middleware, router
│   ├── core/
│   │   ├── config.py          # Settings, env vars, JWT config
│   │   └── database.py        # Engine, session, dependency get_db()
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── routers.py
│   │   │   ├── schemas.py
│   │   │   └── services.py
│   │   └── profile/
│   │       ├── __init__.py
│   │       ├── models.py
│   │       ├── routers.py
│   │       ├── schemas.py
│   │       └── services.py
│   └── shared_models.py       # Tổng hợp metadata cho migration
├── alembic/
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── .env
└── requirements.txt
```

### Quy tắc tổ chức mã
- `routers.py` chỉ xử lý HTTP layer, validate input cơ bản và gọi service.
- `services.py` chứa business logic.
- `models.py` chứa SQLAlchemy models.
- `schemas.py` chứa request/response schema.
- Không import chéo lộn xộn giữa các module nếu chưa cần thiết.

---

## 3. Thiết kế cơ sở dữ liệu cốt lõi
### 3.1. Bảng `users`
Quản lý tài khoản đăng nhập.

Các trường tối thiểu:
- `id`: khóa chính
- `email`: unique, index
- `password_hash`: có thể `NULL` nếu dùng social login
- `auth_provider`: mặc định `local`, hỗ trợ `google`
- `role`: mặc định `customer`, có thể mở rộng `kol`, `admin`
- `is_active`: boolean

Quan hệ:
- Một `users` có một `user_profiles` theo quan hệ 1-1 (`uselist=False`).

### 3.2. Bảng `user_profiles`
Lưu thông tin hồ sơ và cấu hình giao diện cá nhân của user.

Quy định:
- `user_id` là khóa chính đồng thời là khóa ngoại tham chiếu `users.id`
- Áp dụng `ondelete="CASCADE"` để xóa profile khi user bị xóa

Các trường gợi ý:
- `theme_mode`: `light`, `dark`, `custom`
- `font_family`: mặc định `Inter`
- `primary_color`: mã màu chính cho button, mặc định `#FF007F`
- `text_color`: màu chữ chính, mặc định `#111111`
- `bg_type`: `color`, `gradient`, `image`
- `bg_value`: giá trị nền tương ứng
- `avatar_style`: `circle`, `square`, `rounded`
- `button_style`: `filled`, `outline`, `shadow`
- `layout_structure`: kiểu `JSONB` để lưu thứ tự và trạng thái block

Giá trị mặc định đề xuất cho `layout_structure`:

```json
[
  { "id": "media_block", "active": true },
  { "id": "booking_block", "active": true },
  { "id": "products_block", "active": true },
  { "id": "affiliate_block", "active": true }
]
```

---

## 4. API và quy tắc xử lý dữ liệu
### 4.1. Đăng ký tài khoản
Khi gọi API đăng ký local, backend phải tạo đồng thời:
- bản ghi `users`
- bản ghi `user_profiles` mặc định

Hai bước này phải nằm trong cùng một transaction. Nếu một bước lỗi thì rollback toàn bộ.

### 4.2. Cập nhật profile
Khi cập nhật profile:
- hỗ trợ partial update
- chỉ ghi đè các trường được gửi lên
- giữ nguyên các giá trị cũ nếu client không truyền

Nếu dùng Pydantic v2, ưu tiên:

```python
payload = schema.model_dump(exclude_unset=True)
```

### 4.3. Validation
- Validate chặt chẽ enum-like fields như `theme_mode`, `bg_type`, `button_style`.
- Validate `layout_structure` đúng shape dữ liệu mong đợi.
- Không tin tưởng dữ liệu màu sắc, URL ảnh, hoặc block ID từ client mà không kiểm tra.

---

## 5. Bảo mật và hạ tầng
- Mật khẩu phải được hash, không lưu plaintext.
- Có thể dùng `passlib[bcrypt]` hoặc giải pháp hash tương đương đang được dự án thống nhất.
- `main.py` phải cấu hình `CORSMiddleware` để cho phép frontend local truy cập trong môi trường dev.
- Không hard-code secrets trong source code; đọc từ biến môi trường.

---

## 6. Nguyên tắc code dành cho Cursor AI
- Đặt file mới đúng module nghiệp vụ trong `app/modules/`.
- Viết code rõ type, rõ flow và hạn chế side effect khó theo dõi.
- Khi thêm schema hoặc model mới, giữ tên nhất quán giữa database, schema và API response.
- Ưu tiên SQLAlchemy 2.0 style thay vì pattern cũ.
- Nếu dự án đang chạy async stack thì không trộn sync DB calls vào cùng flow.

---

## 7. Tiêu chí hoàn thành phase 1
- Có auth local cơ bản.
- Có cấu trúc user và profile tách riêng.
- Có API đọc/cập nhật profile.
- Có lưu được `layout_structure` bằng `JSONB`.
- Có transaction an toàn ở luồng đăng ký.
- Có CORS để frontend local gọi API thuận lợi.
