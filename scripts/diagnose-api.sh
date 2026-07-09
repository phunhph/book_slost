#!/usr/bin/env bash
# Chẩn đoán vì sao API không chạy trên port 8000.
set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/www/xuong/book_slost}"
BACKEND="${APP_ROOT}/backend"
SERVICE_NAME="${SERVICE_NAME:-book-slost-api}"

echo "==== 1. Service status ===="
systemctl status "${SERVICE_NAME}" --no-pager 2>&1 || true

echo ""
echo "==== 2. Journal (last 40 lines) ===="
journalctl -u "${SERVICE_NAME}" -n 40 --no-pager 2>&1 || true

echo ""
echo "==== 3. Port 8000 ===="
ss -tlnp | grep ':8000' || echo "(không có process lắng nghe 8000)"

echo ""
echo "==== 4. Files ===="
ls -la "${BACKEND}/.env" 2>&1 || echo "MISSING .env"
ls -la "${BACKEND}/.venv/bin/uvicorn" 2>&1 || echo "MISSING .venv"

echo ""
echo "==== 5. PostgreSQL ===="
systemctl is-active postgresql 2>&1 || systemctl is-active postgresql@* 2>&1 || echo "postgresql service?"

echo ""
echo "==== 6. Import app as www-data ===="
if id www-data &>/dev/null; then
  sudo -u www-data env PATH="${BACKEND}/.venv/bin:$PATH" \
    bash -c "cd '${BACKEND}' && python -c 'from app.main import app; print(\"import OK\")'" 2>&1 \
    || echo "www-data KHÔNG import được app (thường do quyền .env / .venv)"
fi

echo ""
echo "==== 7. Import app as root ===="
env PATH="${BACKEND}/.venv/bin:$PATH" \
  bash -c "cd '${BACKEND}' && python -c 'from app.main import app; print(\"import OK\")'" 2>&1 \
  || echo "root cũng không import được — kiểm tra .env / DB"

echo ""
echo "==== Gợi ý sửa ===="
echo "  sudo bash ${APP_ROOT}/scripts/install-api-service.sh ${APP_ROOT} www-data"
echo "  # hoặc nếu deploy bằng root:"
echo "  sudo bash ${APP_ROOT}/scripts/install-api-service.sh ${APP_ROOT} root"
