set -e

PB_VERSION=${1:-0.30.1}
IMAGE_NAME=${2:-pocketbase}
IMAGE_TAG=${3:-latest}

echo "[i] Starting PocketBase Docker image build..."
echo "   PocketBase Version : $PB_VERSION"
echo "   Image Name         : $IMAGE_NAME"
echo "   Image Tag          : $IMAGE_TAG"

docker build \
  --build-arg PB_VERSION=$PB_VERSION \
  --build-arg TARGETOS=linux \
  --build-arg TARGETARCH=amd64 \
  -t "${IMAGE_NAME}:${IMAGE_TAG}" .

if [ $? -eq 0 ]; then
    echo -e "[✓] Build completed: ${IMAGE_NAME}:${IMAGE_TAG}\n"
    echo "[i] Example to run the container:"
    echo "   docker run -d --name pocketbase -p 8090:8090 -v \$(pwd)/pb_data:/pb/pb_data ${IMAGE_NAME}:${IMAGE_TAG}"
else
    echo "[X] Build failed"
    exit $?
fi