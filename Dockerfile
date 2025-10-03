FROM alpine:3.20 AS builder
ARG PB_VERSION=0.22.16
ARG TARGETOS=linux
ARG TARGETARCH=amd64
WORKDIR /tmp
RUN apk add --no-cache curl unzip
RUN curl -L -o pb.zip \
    https://github.com/pocketbase/pocketbase/releases/download/v${PB_VERSION}/pocketbase_${PB_VERSION}_${TARGETOS}_${TARGETARCH}.zip \
    && unzip pb.zip -d /out

FROM alpine:3.20
RUN apk add --no-cache ca-certificates tzdata && \
    adduser -D -H -u 10001 pocketbase
ENV TZ=Asia/Seoul
WORKDIR /pb

RUN mkdir -p /pb/pb_data /pb/pb_public /pb/pb_migrations /pb/pb_hooks && \
    chown -R pocketbase /pb

COPY --from=builder /out/pocketbase /usr/local/bin/pocketbase

VOLUME ["/pb/pb_data"]

EXPOSE 8090
USER pocketbase

CMD ["pocketbase", "serve", "--http", "0.0.0.0:8090", "--dir", "/pb/pb_data", "--publicDir", "/pb/pb_public"]
