#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/xuong/book_slost}"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
SERVICE_NAME="${SERVICE_NAME:-book-slost-api}"
cd "$APP_ROOT"

require_file() {
  if [[ ! -f "$1" ]]; then
    echo "ERROR: Missing $1 — create on VPS before deploy (see docs/VPS_DEPLOY.md)."
    exit 1
  fi
}

require_frontend_env() {
  local dir="$1"
  local name="$2"
  if [[ -f "${dir}/.env" ]]; then
    echo "  OK ${name}: .env"
    return 0
  fi
  if [[ -f "${dir}/.env.production" ]]; then
    echo "  OK ${name}: .env.production"
    return 0
  fi
  echo "ERROR: Missing ${dir}/.env (hoặc .env.production) — tạo trên VPS trước khi deploy."
  exit 1
}

show_api_logs() {
  echo "---- systemctl status ${SERVICE_NAME} ----"
  sudo systemctl status "${SERVICE_NAME}" --no-pager || true
  echo "---- journalctl ${SERVICE_NAME} (last 50 lines) ----"
  sudo journalctl -u "${SERVICE_NAME}" -n 50 --no-pager || true
}

echo "==> Git pull (${DEPLOY_BRANCH})"
git fetch origin "${DEPLOY_BRANCH}"
git reset --hard "origin/${DEPLOY_BRANCH}"

echo "==> Check env files"
require_frontend_env "${APP_ROOT}/admin_frontend" "admin"
require_frontend_env "${APP_ROOT}/client_frontend" "client"
require_frontend_env "${APP_ROOT}/kol_frontend" "kol"
require_file "${APP_ROOT}/backend/.env"

if ! systemctl list-unit-files "${SERVICE_NAME}.service" &>/dev/null; then
  echo "ERROR: Chưa có systemd service ${SERVICE_NAME}."
  echo "Chạy trên VPS (một lần):"
  echo "  sudo cp ${APP_ROOT}/scripts/book-slost-api.service /etc/systemd/system/"
  echo "  sudo systemctl daemon-reload && sudo systemctl enable --now ${SERVICE_NAME}"
  exit 1
fi

echo "==> Backend: deps + migrate"
cd "${APP_ROOT}/backend"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
deactivate
mkdir -p uploads/payment_proofs

echo "==> Backend permissions (service chạy user www-data)"
sudo chown -R www-data:www-data "${APP_ROOT}/backend/.venv" "${APP_ROOT}/backend/uploads"
sudo chmod -R u+rX "${APP_ROOT}/backend/app"

echo "==> Build admin"
cd "${APP_ROOT}/admin_frontend"
npm ci
npm run build

echo "==> Build client"
cd "${APP_ROOT}/client_frontend"
npm ci
npm run build

echo "==> Build kol"
cd "${APP_ROOT}/kol_frontend"
npm ci
npm run build

echo "==> Restart API + reload Nginx"
sudo systemctl daemon-reload
if ! sudo systemctl restart "${SERVICE_NAME}"; then
  show_api_logs
  exit 1
fi
sudo systemctl reload nginx

echo "==> Health check (retry)"
health_ok=0
for attempt in 1 2 3 4 5 6; do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
    curl -fsS http://127.0.0.1:8000/health
    echo ""
    health_ok=1
    break
  fi
  echo "  attempt ${attempt}/6 — API chưa sẵn sàng, đợi 3s..."
  sleep 3
done

if [[ "$health_ok" -ne 1 ]]; then
  echo "ERROR: API không lắng nghe 127.0.0.1:8000"
  show_api_logs
  exit 1
fi

echo "Deploy OK — $(git rev-parse --short HEAD)"
