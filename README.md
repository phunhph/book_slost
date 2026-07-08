# book_slost

Fullstack affiliate + booking platform voi 3 frontend Vue 3 tach role.

## Kien truc

| App | Port | Stack | Vai tro |
|-----|------|-------|---------|
| `admin_frontend` | 3000 | Vue 3 + Vite | Backoffice SB Admin: quan ly danh sach KOL, khach hang, booking |
| `kol_frontend` | 3002 | Vue 3 + Vite | Workspace KOL: custom profile, booking, calendar, lich su, bao cao |
| `client_frontend` | 3001 | Vue 3 + Vite | Public site: danh sach KOL, profile custom, dat lich |
| `backend` | 8000 | FastAPI + PostgreSQL | API, auth, booking, profile |

## Phan quyen

| Role | App | Quyen chinh |
|------|-----|-------------|
| `admin` | Admin (3000) | Xem dashboard, danh sach KOL/khach/booking |
| `kol` | KOL workspace (3002) | Sua profile, nhan booking, calendar, bao cao |
| `customer` | Client (3001) | Xem KOL, dat lich, autofill thong tin khi da login |
| Vang lai | Client (3001) | Xem KOL, dat lich bang SDT/Zalo/Messenger |

## Tai khoan seed (local/dev)

| Role | Email | Mat khau | Username |
|------|-------|----------|----------|
| admin | `admin@example.com` | `Admin@123` | `admin-demo` |
| kol | `creator@example.com` | `Creator@123` | `creator-demo` |
| customer | `customer@example.com` | `Customer@123` | `customer-demo` |

## Chay backend

```powershell
cd backend
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Chay frontend

### Mot lenh (client 3001 + KOL 3002)

```powershell
# Tu thu muc goc repo
npm install
npm run install:frontends
npm run dev
```

### Mot lenh (ca 3 frontend)

```powershell
npm install
npm run install:all
npm run dev:all
```

### Tung app rieng

```powershell
# Admin backoffice
cd admin_frontend
npm install
npm run dev

# KOL workspace
cd kol_frontend
npm install
npm run dev

# Public client
cd client_frontend
npm install
npm run dev
```

URLs:
- Admin: http://localhost:3000
- Client: http://localhost:3001
- KOL: http://localhost:3002
- API: http://localhost:8000

## Env frontend

Moi app co `.env.example`. Copy thanh `.env` hoac `.env.local`:

```env
VITE_API_URL=http://localhost:8000/api
VITE_API_BASE_URL=http://localhost:8000
```

## API chinh

### Auth
- `POST /api/auth/login-local`
- `POST /api/auth/register-local`
- `GET /api/auth/me`
- `GET /auth/google?app=admin|kol|client`
- `GET /auth/callback`

### Admin (role admin)
- `GET /api/admin/dashboard`
- `GET /api/admin/kols`
- `GET /api/admin/customers`
- `GET /api/admin/bookings`

### KOL (role kol)
- `GET /api/kol/dashboard`
- `GET /api/kol/bookings`
- `PATCH /api/kol/bookings/{id}`

### Public / Booking
- `GET /api/public/kols`
- `GET /api/profiles/public/{username}`
- `POST /api/bookings` (guest hoac Bearer token)

## Luong booking

1. Khach vao `client_frontend` -> chon KOL -> xem profile custom
2. Chua login: nhap SDT (bat buoc), Zalo, Messenger, thoi gian dat
3. Da login: he thong tu lay phone/zalo/messenger tu profile
4. KOL xem booking tai `kol_frontend` -> calendar / lich su / cap nhat trang thai
5. Admin xem toan bo tai `admin_frontend`

## Test nhanh

1. `alembic upgrade head`
2. Chay backend + 3 frontend
3. Admin login: `admin@example.com` / `Admin@123`
4. KOL login: `creator@example.com` / `Creator@123`
5. Client: mo http://localhost:3001 -> xem `creator-demo` -> dat lich
6. Customer login: `customer@example.com` / `Customer@123` -> dat lich autofill

## CI/CD

- `.github/workflows/ci.yml`: pytest backend + build 3 frontend Vue
- `.github/workflows/docker-build.yml`: build Docker images backend + admin + kol + client
