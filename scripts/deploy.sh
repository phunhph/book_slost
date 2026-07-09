#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/xuong/book_slost}"
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
