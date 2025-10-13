#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$IMAGE        = "pocketbase"
$CONTAINER    = "pocketbase"
$HOST_PORT    = 8090
$PB_PORT      = 8090
$DATA_DIR     = "./pb_data"
$HOOKS_DIR    = "./api"
$MIGRATIONS_DIR = "./migrations"
$TZ_REGION    = "Asia/Seoul"

Write-Host "[i] Prepare directories"
New-Item -ItemType Directory -Force -Path $DATA_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $HOOKS_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $MIGRATIONS_DIR | Out-Null

$DATA_ABS      = (Resolve-Path $DATA_DIR).Path
$HOOKS_ABS     = (Resolve-Path $HOOKS_DIR).Path
$MIGRATIONS_ABS = (Resolve-Path $MIGRATIONS_DIR).Path

Write-Host "[i] Cleanup existing container (if any)"
docker rm -f $CONTAINER | Out-Null

$HTTP_ADDR = "0.0.0.0:$PB_PORT"

Write-Host "[i] Run PocketBase container"
docker run -d `
  --name $CONTAINER `
  --entrypoint /usr/local/bin/pocketbase `
  -p "$HOST_PORT`:$PB_PORT" `
  -e "TZ=$TZ_REGION" `
  --env-file .env `
  -v "${DATA_ABS}:/pb/pb_data" `
  -v "${HOOKS_ABS}:/pb/pb_hooks" `
  -v "${MIGRATIONS_ABS}:/pb/pb_migrations" `
  --restart unless-stopped `
  $IMAGE `
  serve --http "$HTTP_ADDR" `
        --dir /pb/pb_data `
        --hooksDir /pb/pb_hooks `
        --hooksPool 4 `
        --hooksWatch `
        --migrationsDir /pb/pb_migrations

Write-Host "[✓] Admin UI: http://localhost:$HOST_PORT/_/"
Write-Host "[✓] Hooks mount: ${HOOKS_ABS}  ->  /pb/pb_hooks"
Write-Host "[✓] Migrations mount: ${MIGRATIONS_ABS}  ->  /pb/pb_migrations"
Write-Host "[i] Logs: docker logs -f $CONTAINER"