param(
    [string]$PB_VERSION = "0.22.16",
    [string]$IMAGE_NAME = "pocketbase",
    [string]$IMAGE_TAG = "latest"
)

Write-Host "[i] Starting PocketBase Docker image build..."
Write-Host "   PocketBase Version : $PB_VERSION"
Write-Host "   Image Name         : $IMAGE_NAME"
Write-Host "   Image Tag          : $IMAGE_TAG"

docker build `
  --build-arg PB_VERSION=$PB_VERSION `
  --build-arg TARGETOS=linux `
  --build-arg TARGETARCH=amd64 `
  -t "${IMAGE_NAME}:${IMAGE_TAG}" .

if ($LASTEXITCODE -eq 0) {
    Write-Host "[✓] Build completed: ${IMAGE_NAME}:${IMAGE_TAG}" -ForegroundColor Green
    Write-Host ""
    Write-Host "[i] Example to run the container:"
    Write-Host "   docker run -d --name pocketbase -p 8090:8090 -v ${PWD}\pb_data:/pb/pb_data ${IMAGE_NAME}:${IMAGE_TAG}"
} else {
    Write-Host "[X] Build failed" -ForegroundColor Red
    exit $LASTEXITCODE
}
