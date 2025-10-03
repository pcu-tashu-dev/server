param(
    [string]$PB_VERSION = "0.22.16",
    [string]$IMAGE_NAME = "pocketbase",
    [string]$IMAGE_TAG = "latest"
)

Write-Host "🔨 PocketBase Docker 이미지 빌드 시작..."
Write-Host "   PocketBase Version : $PB_VERSION"
Write-Host "   Image Name         : $IMAGE_NAME"
Write-Host "   Image Tag          : $IMAGE_TAG"

docker build `
  --build-arg PB_VERSION=$PB_VERSION `
  --build-arg TARGETOS=linux `
  --build-arg TARGETARCH=amd64 `
  -t "${IMAGE_NAME}:${IMAGE_TAG}" .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 빌드 완료: ${IMAGE_NAME}:${IMAGE_TAG}" -ForegroundColor Green
    Write-Host ""
    Write-Host "👉 컨테이너 실행 예시:"
    Write-Host "   docker run -d --name pocketbase -p 8090:8090 -v ${PWD}\pb_data:/pb/pb_data ${IMAGE_NAME}:${IMAGE_TAG}"
} else {
    Write-Host "❌ 빌드 실패" -ForegroundColor Red
    exit $LASTEXITCODE
}
