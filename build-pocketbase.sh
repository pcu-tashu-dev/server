set -e

PB_VERSION=${1:-0.22.16}
IMAGE_NAME=${2:-pocketbase}
IMAGE_TAG=${3:-latest}

echo "🔨 PocketBase Docker 이미지 빌드 시작..."
echo "   PocketBase Version : $PB_VERSION"
echo "   Image Name         : $IMAGE_NAME"
echo "   Image Tag          : $IMAGE_TAG"

docker build \
  --build-arg PB_VERSION=$PB_VERSION \
  --build-arg TARGETOS=linux \
  --build-arg TARGETARCH=amd64 \
  -t $IMAGE_NAME:$IMAGE_TAG .

echo "✅ 빌드 완료: $IMAGE_NAME:$IMAGE_TAG"
echo ""
echo "👉 컨테이너 실행 예시:"
echo "   docker run -d --name pocketbase -p 8090:8090 -v \$(pwd)/pb_data:/pb/pb_data $IMAGE_NAME:$IMAGE_TAG"