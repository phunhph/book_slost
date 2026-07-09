# Deploy `book_slost` lên VPS (decodeareer.id.vn)

Hướng dẫn **2 giai đoạn**:

1. **Giai đoạn 1** — Chạy được trên VPS (deploy tay lần đầu)
2. **Giai đoạn 2** — Hoàn thiện deploy tự động bằng **GitHub Actions CI/CD**

---

## Danh sách domain (4 subdomain — bắt buộc)

Tất cả trỏ **A record** về cùng **IP VPS**:

| # | Subdomain | URL đầy đủ | Vai trò |
|---|-----------|------------|---------|
| 1 | `admin` | `https://admin.decodeareer.id.vn` | Màn Admin |
| 2 | `client` | `https://client.decodeareer.id.vn` | Màn khách hàng |
| 3 | `kol` | `https://kol.decodeareer.id.vn` | Màn KOL |
| 4 | `api` | `https://api.decodeareer.id.vn` | Backend API (FastAPI) |

> **Quan trọng:** `api` không phải tùy chọn — 3 màn frontend đều gọi API qua domain này.

---

## Tổng quan kiến trúc

| Domain | App | Thư mục / dịch vụ trên VPS |
|--------|-----|----------------------------|
| `https://admin.decodeareer.id.vn` | Admin backoffice | `/var/www/xuong/book_slost/admin_frontend/dist` |
| `https://client.decodeareer.id.vn` | Client (khách) | `/var/www/xuong/book_slost/client_frontend/dist` |
| `https://kol.decodeareer.id.vn` | KOL workspace | `/var/www/xuong/book_slost/kol_frontend/dist` |
| `https://api.decodeareer.id.vn` | FastAPI backend | `uvicorn` `127.0.0.1:8000` (Nginx reverse proxy) |

Thư mục gốc trên VPS (theo ảnh bạn gửi):

```text
/var/www/xuong/book_slost/
├── admin_frontend/
├── client_frontend/
├── kol_frontend/
├── backend/
└── README.md
```

Nếu trên server còn folder `fromt_be` / `fromt_fe` (lỗi đánh máy cũ), **không dùng** — dùng đúng tên `client_frontend`, `kol_frontend` như repo.

---

## Yêu cầu VPS

- Ubuntu 22.04 / 24.04 (khuyến nghị)
- RAM tối thiểu **2 GB** (4 GB ổn hơn khi build frontend)
- Mở port: **22**, **80**, **443**
- DNS: tạo **4 A record** (xem bảng ở đầu doc):
  - `admin.decodeareer.id.vn`
  - `client.decodeareer.id.vn`
  - `kol.decodeareer.id.vn`
  - `api.decodeareer.id.vn`

---

# GIAI ĐOẠN 1 — Chạy được trên VPS (deploy tay)

## Bước 1. Cài package cơ bản

SSH vào VPS:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl nginx certbot python3-certbot-nginx \
  postgresql postgresql-contrib python3-venv python3-pip
```

Cài Node.js 20 (build frontend):

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node -v
npm -v
```

## Bước 2. Khai báo DNS (bắt buộc — làm trước HTTPS)

Vào panel quản lý domain `decodeareer.id.vn` (Cloudflare, Namecheap, nhà cung cấp domain…), tạo **4 bản ghi A**:

| Host / Name | Type | Value | TTL |
|-------------|------|-------|-----|
| `admin` | A | `<IP_VPS>` | Auto / 300 |
| `client` | A | `<IP_VPS>` | Auto / 300 |
| `kol` | A | `<IP_VPS>` | Auto / 300 |
| `api` | A | `<IP_VPS>` | Auto / 300 |

> **Không bỏ quên `api`** — thiếu record này sẽ lỗi `DNS_PROBE_FINISHED_NXDOMAIN` khi mở `api.decodeareer.id.vn`.

Kiểm tra DNS đã trỏ đúng (chạy trên máy local hoặc VPS):

```bash
nslookup admin.decodeareer.id.vn
nslookup client.decodeareer.id.vn
nslookup kol.decodeareer.id.vn
nslookup api.decodeareer.id.vn
```

Tất cả phải trả về **cùng IP VPS**. Đợi 5–30 phút (đôi khi vài giờ) nếu vừa mới thêm record.

Mở firewall trên VPS (nếu dùng `ufw`):

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'   # mở port 80 + 443
sudo ufw enable
sudo ufw status
```

## Bước 3. Clone / cập nhật code

```bash
sudo mkdir -p /var/www/xuong
sudo chown -R $USER:$USER /var/www/xuong

cd /var/www/xuong
git clone <URL_REPO_GITHUB> book_slost
# Hoặc nếu đã có sẵn:
cd /var/www/xuong/book_slost
git pull origin main
```

## Bước 4. PostgreSQL

```bash
sudo -u postgres psql
```

Trong `psql`:

```sql
CREATE USER book_slost WITH PASSWORD 'MAT_KHAU_MANH_O_DAY';
CREATE DATABASE affiliate_booking_core OWNER book_slost;
\q
```

## Bước 5. Cấu hình backend `.env`

```bash
cd /var/www/xuong/book_slost/backend
cp .env.example .env
nano .env
```

Nội dung mẫu production:

```env
APP_ENV=production
APP_DEBUG=false

POSTGRES_USER=book_slost
POSTGRES_PASSWORD=MAT_KHAU_MANH_O_DAY
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=affiliate_booking_core

JWT_SECRET_KEY=<chuoi-ngau-nhien-dai-64-ky-tu>

ADMIN_FRONTEND_URL=https://admin.decodeareer.id.vn
CLIENT_FRONTEND_URL=https://client.decodeareer.id.vn
KOL_FRONTEND_URL=https://kol.decodeareer.id.vn

CORS_ORIGINS=https://admin.decodeareer.id.vn,https://client.decodeareer.id.vn,https://kol.decodeareer.id.vn

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=https://api.decodeareer.id.vn/auth/callback
```

Chạy migration + tạo thư mục upload bill:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
mkdir -p uploads/payment_proofs
chmod -R 755 uploads
```

## Bước 6. Systemd cho API (chạy nền)

```bash
sudo nano /etc/systemd/system/book-slost-api.service
```

```ini
[Unit]
Description=book_slost FastAPI
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/xuong/book_slost/backend
Environment=PATH=/var/www/xuong/book_slost/backend/.venv/bin
ExecStart=/var/www/xuong/book_slost/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo chown -R www-data:www-data /var/www/xuong/book_slost/backend/uploads
sudo systemctl daemon-reload
sudo systemctl enable book-slost-api
sudo systemctl start book-slost-api
sudo systemctl status book-slost-api
```

Kiểm tra API:

```bash
curl http://127.0.0.1:8000/health
# Kỳ vọng: {"status":"ok"}
```

## Bước 7. Env & build 3 frontend (production)

Vite đọc biến lúc **build** (`npm run build`), không đọc lúc runtime trên Nginx.  
Tạo file **`.env.production`** trong từng folder frontend **trên VPS** (không commit lên Git).

### Bảng biến môi trường

| Biến | Admin | Client | KOL | Mô tả |
|------|:-----:|:------:|:---:|-------|
| `VITE_API_URL` | ✅ | ✅ | ✅ | URL API có `/api` — gọi REST |
| `VITE_API_BASE_URL` | ✅ | ✅ | ✅ | URL gốc API — OAuth redirect |
| `VITE_CLIENT_APP_URL` | — | ✅ | ✅ | Link sang màn client |
| `VITE_KOL_APP_URL` | — | ✅ | — | Link sang màn KOL (redirect sau login) |
| `VITE_ADMIN_APP_URL` | — | ✅ | — | Link sang màn admin (redirect sau login) |

### Admin — `admin_frontend/.env.production`

```bash
cd /var/www/xuong/book_slost/admin_frontend
cat > .env.production << 'EOF'
VITE_API_URL=https://api.decodeareer.id.vn/api
VITE_API_BASE_URL=https://api.decodeareer.id.vn
EOF
npm ci
npm run build
```

### Client — `client_frontend/.env.production`

```bash
cd /var/www/xuong/book_slost/client_frontend
cat > .env.production << 'EOF'
VITE_API_URL=https://api.decodeareer.id.vn/api
VITE_API_BASE_URL=https://api.decodeareer.id.vn
VITE_CLIENT_APP_URL=https://client.decodeareer.id.vn
VITE_KOL_APP_URL=https://kol.decodeareer.id.vn
VITE_ADMIN_APP_URL=https://admin.decodeareer.id.vn
EOF
npm ci
npm run build
```

### KOL — `kol_frontend/.env.production`

```bash
cd /var/www/xuong/book_slost/kol_frontend
cat > .env.production << 'EOF'
VITE_API_URL=https://api.decodeareer.id.vn/api
VITE_API_BASE_URL=https://api.decodeareer.id.vn
VITE_CLIENT_APP_URL=https://client.decodeareer.id.vn
EOF
npm ci
npm run build
```

> **Lưu ý:** Sau khi tạo `.env.production` trên VPS, mỗi lần `scripts/deploy.sh` chạy sẽ `npm run build` lại — file env **phải giữ trên server**, không bị ghi đè bởi `git pull`.

### Dev local (tham khảo)

| App | File | Port |
|-----|------|------|
| Admin | `admin_frontend/.env` | 3000 |
| Client | `client_frontend/.env` | 3001 |
| KOL | `kol_frontend/.env` | 3002 |

Copy từ `.env.example` tương ứng, dùng `http://localhost:8000` cho API.

Sau build, mỗi app có thư mục `dist/` — Nginx sẽ trỏ vào đó.

## Bước 8. Nginx — HTTP (port 80, chuẩn bị cho HTTPS)

### API — `/etc/nginx/sites-available/api.decodeareer.id.vn`

```nginx
server {
    listen 80;
    server_name api.decodeareer.id.vn;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Admin — `/etc/nginx/sites-available/admin.decodeareer.id.vn`

```nginx
server {
    listen 80;
    server_name admin.decodeareer.id.vn;
    root /var/www/xuong/book_slost/admin_frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Client — `/etc/nginx/sites-available/client.decodeareer.id.vn`

```nginx
server {
    listen 80;
    server_name client.decodeareer.id.vn;
    root /var/www/xuong/book_slost/client_frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### KOL — `/etc/nginx/sites-available/kol.decodeareer.id.vn`

```nginx
server {
    listen 80;
    server_name kol.decodeareer.id.vn;
    root /var/www/xuong/book_slost/kol_frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Bật site:

```bash
sudo ln -sf /etc/nginx/sites-available/api.decodeareer.id.vn /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/admin.decodeareer.id.vn /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/client.decodeareer.id.vn /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/kol.decodeareer.id.vn /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Kiểm tra HTTP (chưa HTTPS) — **phải OK trước khi chạy Certbot**:

```bash
curl -I http://api.decodeareer.id.vn/health
curl -I http://admin.decodeareer.id.vn
```

Nếu `curl` báo không resolve host → quay lại **Bước 2 DNS**.  
Nếu `502` → kiểm tra `book-slost-api` (Bước 6).

## Bước 9. Khai báo HTTPS (Let's Encrypt + Certbot)

Sau khi **4 domain resolve DNS** và **Nginx HTTP chạy OK**, cấp chứng chỉ SSL miễn phí:

```bash
sudo certbot --nginx \
  -d api.decodeareer.id.vn \
  -d admin.decodeareer.id.vn \
  -d client.decodeareer.id.vn \
  -d kol.decodeareer.id.vn \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email
```

Khi Certbot hỏi **redirect HTTP → HTTPS**, chọn **`2` (Redirect)** — khuyến nghị bắt buộc cho production.

Certbot sẽ tự:
- Tạo file SSL trong `/etc/letsencrypt/live/...`
- Sửa config Nginx: thêm `listen 443 ssl`, certificate, redirect `80 → 443`

Kiểm tra HTTPS:

```bash
curl -I https://api.decodeareer.id.vn/health
curl https://api.decodeareer.id.vn/health
```

Kỳ vọng: HTTP `200` và body `{"status":"ok"}`.

Mở trình duyệt (phải dùng **`https://`**, không phải `http://`):

- `https://api.decodeareer.id.vn/health`
- `https://admin.decodeareer.id.vn`
- `https://client.decodeareer.id.vn`
- `https://kol.decodeareer.id.vn`

Gia hạn SSL tự động (Let's Encrypt 90 ngày):

```bash
sudo certbot renew --dry-run
```

### Lỗi HTTPS thường gặp

| Lỗi | Nguyên nhân | Cách xử lý |
|-----|-------------|------------|
| `DNS_PROBE_FINISHED_NXDOMAIN` | Chưa có DNS `api` (hoặc domain khác) | Thêm A record ở **Bước 2** |
| Certbot `Connection refused` | Port 80 chưa mở / Nginx chưa chạy | `sudo ufw allow 'Nginx Full'`; `sudo systemctl status nginx` |
| Certbot `404` validation | `server_name` Nginx sai domain | Sửa lại config Bước 8, `nginx -t`, reload |
| `NET::ERR_CERT_COMMON_NAME_INVALID` | Truy cập IP thay vì domain | Dùng đúng URL `https://api.decodeareer.id.vn` |
| Frontend gọi API lỗi mixed content | Build FE với `http://` API | `.env.production` phải dùng `https://api...` (Bước 7) |

## Bước 10. Kiểm tra sau deploy tay

| URL | Kỳ vọng |
|-----|---------|
| `https://api.decodeareer.id.vn/health` | `{"status":"ok"}` |
| `https://admin.decodeareer.id.vn` | Trang login admin |
| `https://client.decodeareer.id.vn` | Trang marketplace KOL |
| `https://kol.decodeareer.id.vn` | Trang login KOL |

Đăng nhập thử (seed):

- Admin: `admin@example.com` / `Admin@123`
- KOL: `creator@example.com` / `Creator@123`
- Client: `customer@example.com` / `Customer@123`

---

# GIAI ĐOẠN 2 — CI/CD deploy tự động (GitHub Actions → VPS)

Repo đã có:

- `.github/workflows/ci.yml` — chạy test + build khi push/PR
- `.github/workflows/docker-build.yml` — chỉ **build image** trong CI (chưa deploy lên VPS)

Mục tiêu: sau khi CI **pass** trên nhánh `main`, tự động SSH vào VPS, `git pull`, build, restart.

## Bước 1. Script deploy trên VPS

Repo đã có sẵn `scripts/deploy.sh`. Sau `git pull` trên VPS, chỉ cần:

```bash
chmod +x /var/www/xuong/book_slost/scripts/deploy.sh
```

Nội dung script (tham khảo):

```bash
#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/var/www/xuong/book_slost"
cd "$APP_ROOT"

echo "==> Git pull"
git fetch origin main
git reset --hard origin/main

echo "==> Backend: deps + migrate"
cd backend
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
deactivate

echo "==> Build admin"
cd "$APP_ROOT/admin_frontend"
npm ci
npm run build

echo "==> Build client"
cd "$APP_ROOT/client_frontend"
npm ci
npm run build

echo "==> Build kol"
cd "$APP_ROOT/kol_frontend"
npm ci
npm run build

echo "==> Restart API"
sudo systemctl restart book-slost-api
sudo systemctl reload nginx

echo "==> Deploy OK"
curl -fsS http://127.0.0.1:8000/health
```

```bash
chmod +x /var/www/xuong/book_slost/scripts/deploy.sh
```

Đảm bảo `.env.production` đã có trong từng frontend (bước 6 giai đoạn 1) — file này **không** commit secret, chỉ nằm trên VPS.

## Bước 2. SSH key cho GitHub Actions

Trên máy local (hoặc VPS):

```bash
ssh-keygen -t ed25519 -C "github-deploy-book-slost" -f deploy_book_slost -N ""
```

- **Public key** (`deploy_book_slost.pub`) → thêm vào VPS:  
  `~/.ssh/authorized_keys` của user deploy (ví dụ `ubuntu` hoặc user bạn dùng)
- **Private key** → lưu vào GitHub Secret

User deploy cần quyền:

```bash
# Cho phép restart service không hỏi mật khẩu (tùy chọn)
sudo visudo
# Thêm dòng:
# deployuser ALL=(ALL) NOPASSWD: /bin/systemctl restart book-slost-api, /bin/systemctl reload nginx
```

## Bước 3. GitHub Secrets

Vào repo GitHub → **Settings → Secrets and variables → Actions**, thêm:

| Secret | Ví dụ |
|--------|--------|
| `VPS_HOST` | IP hoặc hostname VPS |
| `VPS_USER` | `ubuntu` |
| `VPS_SSH_KEY` | Nội dung private key |
| `VPS_PORT` | `22` (optional) |
| `VPS_APP_PATH` | `/var/www/xuong/book_slost` |

## Bước 4. Workflow deploy

Repo đã có `.github/workflows/deploy-vps.yml`. Chỉ cần cấu hình GitHub Secrets (bước 3), push lên `main` là workflow tự chạy sau CI.

Nội dung workflow (tham khảo):

```yaml
name: Deploy VPS

on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main, master]
  workflow_dispatch:

concurrency:
  group: deploy-vps
  cancel-in-progress: true

jobs:
  deploy:
    if: >
      github.event_name == 'workflow_dispatch' ||
      (github.event_name == 'workflow_run' && github.event.workflow_run.conclusion == 'success')
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.2.0
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          port: ${{ secrets.VPS_PORT || 22 }}
          script: |
            cd ${{ secrets.VPS_APP_PATH }}
            ./scripts/deploy.sh
```

Luồng:

```text
git push main → CI (test + build) → success → Deploy VPS (SSH + deploy.sh)
```

## Bước 5. Google OAuth (nếu dùng)

Trong Google Cloud Console, thêm **Authorized redirect URI**:

- `https://api.decodeareer.id.vn/auth/callback`

Và callback frontend (theo từng app):

- `https://admin.decodeareer.id.vn/auth/google/callback`
- `https://client.decodeareer.id.vn/auth/google/callback`
- `https://kol.decodeareer.id.vn/auth/google/callback`

---

## Checklist nhanh

### Lần đầu (tay)

- [ ] **Bước 2:** DNS 4 subdomain (`admin`, `client`, `kol`, `api`) → IP VPS
- [ ] `nslookup` 4 domain OK
- [ ] PostgreSQL + `backend/.env` (URL `https://`)
- [ ] `alembic upgrade head`
- [ ] systemd `book-slost-api` chạy OK
- [ ] `.env.production` 3 frontend (`https://api...`)
- [ ] Build 3 frontend
- [ ] Nginx HTTP (Bước 8) — `curl http://...` OK
- [ ] **Bước 9:** Certbot HTTPS + redirect 80→443
- [ ] `curl https://api.decodeareer.id.vn/health` OK
- [ ] Login + đặt lịch + upload bill thử

### CI/CD

- [ ] `scripts/deploy.sh` trên VPS
- [ ] SSH key + GitHub Secrets
- [ ] `.github/workflows/deploy-vps.yml`
- [ ] Push `main` → CI xanh → deploy tự chạy

---

## Xử lý lỗi thường gặp

| Triệu chứng | Cách xử lý |
|-------------|------------|
| Frontend báo "Failed to fetch" | Kiểm tra `VITE_API_URL` dùng `https://`; DNS `api` OK; CORS trong `backend/.env` |
| `DNS_PROBE_FINISHED_NXDOMAIN` | Chưa khai báo DNS — làm **Bước 2**, đợi propagate |
| HTTPS không có / cert lỗi | Chạy **Bước 9** Certbot sau khi HTTP OK |
| 502 Bad Gateway API | `sudo systemctl status book-slost-api`; xem log `journalctl -u book-slost-api -f` |
| Vue route F5 bị 404 | Nginx cần `try_files ... /index.html` |
| Upload bill lỗi | `client_max_body_size 10M`; quyền `backend/uploads` cho `www-data` |
| OAuth Google lỗi | Sai `GOOGLE_REDIRECT_URI` hoặc chưa khai báo URL trên Google Console |

---

## Ghi chú bảo mật production

- Đổi `JWT_SECRET_KEY` và mật khẩu DB — **không** dùng giá trị demo
- `APP_DEBUG=false`
- Không commit `.env` / `.env.production` lên Git
- Chỉ lưu **email** khi "Ghi nhớ đăng nhập" (không lưu mật khẩu plain text)
- Backup Postgres định kỳ: `pg_dump affiliate_booking_core > backup.sql`
