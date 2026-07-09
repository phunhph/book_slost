#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/xuong/book_slost}"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
cd "$APP_ROOT"

require_file() {
  if [[ ! -f "$1" ]]; then
    echo "ERROR: Missing $1 — create on VPS before deploy (see docs/VPS_DEPLOY.md Bước 7)."
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

echo "==> Git pull (${DEPLOY_BRANCH})"
git fetch origin "${DEPLOY_BRANCH}"
git reset --hard "origin/${DEPLOY_BRANCH}"

echo "==> Check env files"
require_frontend_env "${APP_ROOT}/admin_frontend" "admin"
require_frontend_env "${APP_ROOT}/client_frontend" "client"
require_frontend_env "${APP_ROOT}/kol_frontend" "kol"
require_file "${APP_ROOT}/backend/.env"

echo "==> Backend: deps + migrate"
cd "${APP_ROOT}/backend"
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
deactivate

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
sudo systemctl restart book-slost-api
sudo systemctl reload nginx

echo "==> Health check"
curl -fsS http://127.0.0.1:8000/health
echo ""
echo "Deploy OK — $(git rev-parse --short HEAD)"
