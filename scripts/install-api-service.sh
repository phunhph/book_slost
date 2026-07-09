#!/usr/bin/env bash
# Cài / cập nhật systemd service cho API.
# Usage: sudo bash scripts/install-api-service.sh [APP_ROOT] [RUN_USER]
set -euo pipefail

APP_ROOT="${1:-/var/www/xuong/book_slost}"
RUN_USER="${2:-www-data}"

SERVICE_PATH="/etc/systemd/system/book-slost-api.service"
BACKEND="${APP_ROOT}/backend"

if [[ ! -f "${BACKEND}/.venv/bin/uvicorn" ]]; then
  echo "ERROR: Chưa có ${BACKEND}/.venv — chạy pip install trong backend trước."
  exit 1
fi

cat > "${SERVICE_PATH}" <<EOF
[Unit]
Description=book_slost FastAPI
After=network.target postgresql.service

[Service]
User=${RUN_USER}
Group=${RUN_USER}
WorkingDirectory=${BACKEND}
Environment=PATH=${BACKEND}/.venv/bin
ExecStart=${BACKEND}/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable book-slost-api
echo "Installed ${SERVICE_PATH} (User=${RUN_USER})"
systemctl restart book-slost-api
sleep 2
systemctl status book-slost-api --no-pager || true
curl -fsS http://127.0.0.1:8000/health && echo "" || echo "Health check failed — xem: journalctl -u book-slost-api -n 30"
