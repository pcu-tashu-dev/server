set -euo pipefail

IMAGE="pocketbase"
CONTAINER="pocketbase"
HOST_PORT="8090"
PB_PORT="8090"
DATA_DIR="./pb_data"
HOOKS_DIR="./api"
MIGRATIONS_DIR="./migrations"
TZ_REGION="Asia/Seoul"

echo "[i] Prepare directories"
mkdir -p "$DATA_DIR" "$HOOKS_DIR" "$MIGRATIONS_DIR"

# Absolute paths
if command -v realpath >/dev/null 2>&1; then
  DATA_ABS="$(realpath "$DATA_DIR")"
  HOOKS_ABS="$(realpath "$HOOKS_DIR")"
  MIGRATIONS_ABS="$(realpath "$MIGRATIONS_DIR")"
else
  DATA_ABS="$(cd "$(dirname "$DATA_DIR")" && pwd)/$(basename "$DATA_DIR")"
  HOOKS_ABS="$(cd "$(dirname "$HOOKS_DIR")" && pwd)/$(basename "$HOOKS_DIR")"
  MIGRATIONS_ABS="$(cd "$(dirname "$MIGRATIONS_DIR")" && pwd)/$(basename "$MIGRATIONS_DIR")"
fi

echo "[i] Cleanup existing container (if any)"
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true

HTTP_ADDR="0.0.0.0:${PB_PORT}"

echo "[i] Run PocketBase container"
docker run -d \
  --name "$CONTAINER" \
  --user "$(id -u):$(id -g)" \
  --entrypoint /usr/local/bin/pocketbase \
  -p "${HOST_PORT}:${PB_PORT}" \
  -e TZ="${TZ_REGION}" \
  -v "${DATA_ABS}:/pb/pb_data" \
  -v "${HOOKS_ABS}:/pb/pb_hooks" \
  -v "${MIGRATIONS_ABS}:/pb/pb_migrations" \
  --restart unless-stopped \
  "${IMAGE}" \
  serve --http "${HTTP_ADDR}" \
        --dir /pb/pb_data \
        --hooksDir /pb/pb_hooks \
        --hooksPool 4 \
        --hooksWatch \
        --migrationsDir /pb/pb_migrations

echo "[✓] Admin UI: http://localhost:${HOST_PORT}/_/"
echo "[✓] Hooks mount: ${HOOKS_ABS}       -> /pb/pb_hooks"
echo "[✓] Migrations mount: ${MIGRATIONS_ABS} -> /pb/pb_migrations"
echo "[i] Logs: docker logs -f ${CONTAINER}"
