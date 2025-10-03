#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$Image     = "pocketbase"
$Container = "pocketbase"
$HostPort  = 8090
$PbPort    = 8090
$DataDir   = "pb_data"
$HooksDir  = "api"
$TimeZone  = "Asia/Seoul"

Write-Host "[i] Prepare directories"
New-Item -ItemType Directory -Force -Path $DataDir | Out-Null
New-Item -ItemType Directory -Force -Path $HooksDir | Out-Null

Write-Host "[i] Cleanup existing container (if any)"
docker rm -f $Container 2>$null | Out-Null

$pwdPath  = (Get-Location).Path
$dataAbs  = Join-Path $pwdPath $DataDir
$hooksAbs = Join-Path $pwdPath $HooksDir
$Http     = "0.0.0.0:$PbPort"

Write-Host "[i] Run PocketBase container"
docker run -d `
  --name $Container `
  --entrypoint /usr/local/bin/pocketbase `
  -p ("{0}:{1}" -f $HostPort, $PbPort) `
  -e TZ=$TimeZone `
  -v ("{0}:/pb_data"  -f $dataAbs) `
  -v ("{0}:/pb_hooks" -f $hooksAbs) `
  --restart unless-stopped `
  $Image `
  serve --http $Http `
        --dir /pb_data `
        --hooksDir /pb_hooks `
        --hooksPool 4 `
        --hooksWatch | Out-Null

Write-Host ("[✓] Admin UI: http://localhost:{0}/_/" -f $HostPort)
Write-Host ("[✓] Hooks mount: {0}  ->  /pb_hooks" -f $hooksAbs)
Write-Host ("[i] Logs: docker logs -f {0}" -f $Container)
