set -euo pipefail

IMAGE="pocketbase"
CONTAINER="pocketbase"
HOST_PORT="8090"
PB_PORT="8090"
DATA_DIR="./pb_data"
HOOKS_DIR="./api"
TZ_REGION="Asia/Seoul"

echo "[i] Prepare directories"
mkdir -p "$DATA_DIR" "$HOOKS_DIR"

echo "[i] Cleanup existing container (if any)"
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true

if command -v realpath >/dev/null 2>&1; then
  DATA_ABS="$(realpath "$DATA_DIR")"
  HOOKS_ABS="$(realpath "$HOOKS_DIR")"
else
  DATA_ABS="$(cd "$(dirname "$DATA_DIR")" && pwd)/$(basename "$DATA_DIR")"
  HOOKS_ABS="$(cd "$(dirname "$HOOKS_DIR")" && pwd)/$(basename "$HOOKS_DIR")"
fi

HTTP_ADDR="0.0.0.0:${PB_PORT}"

echo "[i] Run PocketBase container"
docker run -d \
  --name "$CONTAINER" \
  --entrypoint /usr/local/bin/pocketbase \
  -p "${HOST_PORT}:${PB_PORT}" \
  -e TZ="${TZ_REGION}" \
  -v "${DATA_ABS}:/pb_data" \
  -v "${HOOKS_ABS}:/pb_hooks" \
  --restart unless-stopped \
  "${IMAGE}" \
  serve --http "${HTTP_ADDR}" \
        --dir /pb_data \
        --hooksDir /pb_hooks \
        --hooksPool 4 \
        --hooksWatch

echo "[✓] Admin UI: http://localhost:${HOST_PORT}/_/"
echo "[✓] Hooks mount: ${HOOKS_ABS}  ->  /pb_hooks"
echo "[i] Logs: docker logs -f ${CONTAINER}"
