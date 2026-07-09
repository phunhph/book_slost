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

### Làm ở đâu? (tóm tắt)

| Bước | Việc | Làm ở đâu |
|------|------|-----------|
| 1 | Cài package, Node, Nginx… | **VPS** (SSH) |
| 2 | DNS + firewall | **Panel domain** + **VPS** |
| 3 → 10 | Clone code, DB, `.env`, build, Nginx, SSL | **VPS** (SSH) |

> Từ **Bước 3** trở đi Giai đoạn 1: **toàn bộ trên VPS**, SSH vào server rồi chạy lệnh.  
> Không cần làm trên máy Windows/local (trừ Bước 2 kiểm tra `nslookup` có thể chạy trên máy bạn).

## Bước 1. Cài package cơ bản — **VPS (SSH)**

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

## Bước 2. Khai báo DNS (bắt buộc — làm trước HTTPS) — **Panel domain** + **VPS**

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

## Bước 3. Clone / cập nhật code — **VPS (SSH)**

```bash
sudo mkdir -p /var/www/xuong
sudo chown -R $USER:$USER /var/www/xuong

cd /var/www/xuong
git clone <URL_REPO_GITHUB> book_slost
# Hoặc nếu đã có sẵn:
cd /var/www/xuong/book_slost
git pull origin main
```

## Bước 4. PostgreSQL — **VPS (SSH)**

```bash
sudo -u postgres psql
```

Trong `psql`:

```sql
CREATE USER book_slost WITH PASSWORD 'MAT_KHAU_MANH_O_DAY';
CREATE DATABASE affiliate_booking_core OWNER book_slost;
\q
```

## Bước 5. Cấu hình backend `.env` — **VPS (SSH)**

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

## Bước 6. Systemd cho API (chạy nền) — **VPS (SSH)**

```bash
sudo cp /var/www/xuong/book_slost/scripts/book-slost-api.service /etc/systemd/system/book-slost-api.service
# Nếu APP_PATH khác, sửa đường dẫn trong file service trước khi copy
sudo systemctl daemon-reload
sudo chown -R www-data:www-data /var/www/xuong/book_slost/backend/uploads
sudo systemctl enable book-slost-api
sudo systemctl start book-slost-api
sudo systemctl status book-slost-api
```

Hoặc tạo tay — `/etc/systemd/system/book-slost-api.service`:

Kiểm tra API:

```bash
curl http://127.0.0.1:8000/health
# Kỳ vọng: {"status":"ok"}
```

## Bước 7. Env & build 3 frontend (production) — **VPS (SSH)**

Vite đọc biến lúc **build** (`npm run build`), không đọc lúc runtime trên Nginx.  
Tạo file **`.env`** hoặc **`.env.production`** trong từng folder frontend **trên VPS** (không commit lên Git).  
Nếu đã có `.env` thì **không cần** `.env.production`.

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

> **Lưu ý:** File env trên VPS (`.env` hoặc `.env.production`) **không bị ghi đè** bởi `git pull` — giữ nguyên sau mỗi deploy.

### Dev local (tham khảo)

| App | File | Port |
|-----|------|------|
| Admin | `admin_frontend/.env` | 3000 |
| Client | `client_frontend/.env` | 3001 |
| KOL | `kol_frontend/.env` | 3002 |

Copy từ `.env.example` tương ứng, dùng `http://localhost:8000` cho API.

Sau build, mỗi app có thư mục `dist/` — Nginx sẽ trỏ vào đó.

## Bước 8. Nginx — HTTP (port 80, chuẩn bị cho HTTPS) — **VPS (SSH)**

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

## Bước 9. Khai báo HTTPS (Let's Encrypt + Certbot) — **VPS (SSH)**

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

## Bước 10. Kiểm tra sau deploy tay — **Trình duyệt** (máy bạn) + **VPS**

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

# GIAI ĐOẠN 2 — CI/CD deploy tự động (MR/PR → `main` → VPS)

> **Điều kiện:** Đã xong **Giai đoạn 1** (site chạy trên VPS).

### Làm ở đâu? (tóm tắt)

| Bước | Việc | Làm ở đâu |
|------|------|-----------|
| 1 | `git pull` OK trên VPS | **VPS** (SSH) |
| 2 | `chmod +x deploy.sh` | **VPS** (SSH) |
| 3 | Tạo SSH key deploy | **Máy local** → public key gắn **VPS**, private key → **GitHub** |
| 4 | Secrets `VPS_HOST`, `VPS_USER`… | **GitHub** (web) |
| 5 | Merge MR, xem Actions | **GitHub** (web) |
| 6 | OAuth URLs (nếu dùng) | **Google Cloud** (web) |

## Luồng deploy

```text
Tạo PR/MR → CI chạy (test + build) → KHÔNG deploy
       ↓
Merge vào main → CI chạy lại trên main
       ↓
CI xanh → job "Deploy VPS" SSH vào server → scripts/deploy.sh
```

| Sự kiện | CI test/build | Deploy VPS |
|---------|:-------------:|:----------:|
| Mở PR / MR vào `main` | ✅ | ❌ |
| Push thẳng lên `main` | ✅ | ✅ (nếu CI xanh) |
| Merge PR/MR vào `main` | ✅ | ✅ (nếu CI xanh) |
| Manual (Actions → Deploy VPS manual) | ❌ | ✅ |

Workflow:
- `.github/workflows/ci.yml` — test + build + **deploy khi push `main`**
- `.github/workflows/deploy-vps.yml` — deploy tay (không cần chạy CI)

## Bước 1. Chuẩn bị VPS cho `git pull` — **VPS (SSH)**

User deploy (ví dụ `ubuntu`) phải pull được code từ GitHub:

```bash
cd /var/www/xuong/book_slost
git remote -v
git pull origin main
```

Nếu repo private, thêm **Deploy key** (GitHub → Settings → Deploy keys) hoặc SSH key của user VPS vào GitHub account.

## Bước 2. Script deploy trên VPS — **VPS (SSH)**

Repo có `scripts/deploy.sh`. Trên VPS:

```bash
chmod +x /var/www/xuong/book_slost/scripts/deploy.sh
```

Script sẽ:
1. `git reset --hard origin/main`
2. Kiểm tra mỗi FE có `.env` **hoặc** `.env.production`; backend có `.env`
3. `pip install` + `alembic upgrade head`
4. `npm ci && npm run build` (admin, client, kol)
5. `systemctl restart book-slost-api` + reload nginx
6. `curl` health check

> `.env` (FE) và `backend/.env` **phải có sẵn trên VPS** — không commit Git.

## Bước 3. SSH key cho GitHub Actions — **Máy local** + **VPS** + **GitHub**

Tạo key trên **máy local** (Windows/PowerShell hoặc Git Bash):

```bash
ssh-keygen -t ed25519 -C "github-deploy-book-slost" -f deploy_book_slost -N ""
```

- **Public key** → VPS `~/.ssh/authorized_keys` (user deploy)
- **Private key** → GitHub Secret `VPS_SSH_KEY`

Cho phép restart service không hỏi mật khẩu — chạy trên **VPS**:

```bash
sudo visudo
# Thêm (đổi ubuntu thành user deploy của bạn):
# ubuntu ALL=(ALL) NOPASSWD: /bin/systemctl restart book-slost-api, /bin/systemctl reload nginx
```

## Bước 4. GitHub Secrets — **GitHub (web)**

Repo → **Settings → Secrets and variables → Actions → Repository secrets**.

Bạn đã tạo đúng **4 secret** sau (tên phải khớp chính xác):

| Secret | Giá trị gợi ý |
|--------|----------------|
| `VPS_HOST` | IP VPS, ví dụ `123.45.67.89` |
| `VPS_USER` | User SSH, ví dụ `ubuntu` |
| `VPS_SSH_KEY` | Toàn bộ nội dung file **private key** |
| `VPS_APP_PATH` | `/var/www/xuong/book_slost` |

Workflow `.github/workflows/ci.yml` (job **Deploy VPS**) và `deploy-vps.yml` (manual) đều dùng 4 biến này — **không cần** secret khác.

> `VPS_SSH_KEY`: paste cả block `-----BEGIN OPENSSH PRIVATE KEY-----` … `-----END OPENSSH PRIVATE KEY-----`

## Bước 5. Kiểm tra sau khi merge MR — **GitHub (web)** + **VPS**

1. Merge PR vào `main` trên GitHub
2. Vào **Actions** → workflow **CI** → run mới nhất
3. Thấy job **Deploy VPS** màu xanh
4. Trên VPS:

```bash
curl https://api.decodeareer.id.vn/health
```

### Deploy tay (không qua merge)

Actions → **Deploy VPS (manual)** → **Run workflow**

## Bước 6. Google OAuth (nếu dùng) — **Google Cloud (web)**

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
- [ ] `.env` hoặc `.env.production` 3 frontend (`https://api...`)
- [ ] Build 3 frontend
- [ ] Nginx HTTP (Bước 8) — `curl http://...` OK
- [ ] **Bước 9:** Certbot HTTPS + redirect 80→443
- [ ] `curl https://api.decodeareer.id.vn/health` OK
- [ ] Login + đặt lịch + upload bill thử

### CI/CD

- [ ] VPS `git pull origin main` OK (deploy key nếu repo private)
- [ ] `chmod +x scripts/deploy.sh`
- [ ] `.env` (FE) + `backend/.env` trên VPS
- [ ] GitHub Secrets: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `VPS_APP_PATH`
- [ ] `sudo visudo` cho restart service
- [ ] Merge MR vào `main` → Actions job **Deploy VPS** xanh

---

## Xử lý lỗi thường gặp

| Triệu chứng | Cách xử lý |
|-------------|------------|
| Frontend báo "Failed to fetch" | Kiểm tra `VITE_API_URL` dùng `https://`; DNS `api` OK; CORS trong `backend/.env` |
| `DNS_PROBE_FINISHED_NXDOMAIN` | Chưa khai báo DNS — làm **Bước 2**, đợi propagate |
| HTTPS không có / cert lỗi | Chạy **Bước 9** Certbot sau khi HTTP OK |
| `curl` 127.0.0.1:8000 fail sau deploy | Service `book-slost-api` chưa tạo hoặc crash | `sudo systemctl status book-slost-api`; `journalctl -u book-slost-api -n 50` |
| API exit ngay sau restart | Sai `.env` DB / thiếu `.venv` | Kiểm tra `backend/.env`; chạy Bước 5–6 thủ công một lần |
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
