# settings.py
from __future__ import annotations
import os
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    tashu_url: str
    tashu_key: str
    openweather_api_key: Optional[str]
    verify_ssl: bool
    ca_bundle: Optional[str]
    http_timeout_connect: float
    http_timeout_read: float
    retry_total: int
    backoff_base: float
    jitter_base: float
    jitter_extra: float
    concurrency: int
    proxy_cooldown: int
    proxy_urls: List[str]
    proxy_list_source_url: Optional[str]
    proxy_refresh_interval: int
    proxy_format: str
    allow_direct: bool
    http_debug: bool
    influx_url: Optional[str]
    influx_org: Optional[str]
    influx_token: Optional[str]
    influx_bucket: Optional[str]
    influx_measurement: str
    influx_weather_measurement: str
    pb_url: Optional[str]
    pb_admin_token: Optional[str]
    pb_station_collection: str
    pb_zone_collection: str


def _env_bool(k: str, default: bool) -> bool:
    v = os.getenv(k)
    if v is None:
        return default
    return v.strip().lower() not in ("0", "false", "no", "off")


def load_settings() -> Settings:
    proxies = os.getenv("PROXY_URLS", "")
    return Settings(
        tashu_url=os.getenv(
            "TASHU_URL", "https://bikeapp.tashu.or.kr:50041/v1/openapi/station"
        ),
        tashu_key=os.getenv("TASHU_KEY", ""),
        openweather_api_key=os.getenv("OPENWEATHER_API_KEY") or None,
        verify_ssl=_env_bool("VERIFY_SSL", False),
        ca_bundle=os.getenv("CA_BUNDLE") or None,
        http_timeout_connect=float(os.getenv("HTTP_TIMEOUT_CONNECT", "5")),
        http_timeout_read=float(os.getenv("HTTP_TIMEOUT_READ", "15")),
        retry_total=int(os.getenv("RETRY_TOTAL", "2")),
        backoff_base=float(os.getenv("BACKOFF_BASE", "0.3")),
        jitter_base=float(os.getenv("JITTER_BASE", "0.1")),
        jitter_extra=float(os.getenv("JITTER_EXTRA", "0.2")),
        concurrency=int(os.getenv("CONCURRENCY", "10")),
        proxy_cooldown=int(os.getenv("PROXY_COOLDOWN", "60")),
        proxy_urls=[p.strip() for p in proxies.split(",") if p.strip()],
        proxy_list_source_url=os.getenv("PROXY_LIST_SOURCE_URL") or None,
        proxy_refresh_interval=int(os.getenv("PROXY_REFRESH_INTERVAL", "300")),
        proxy_format=os.getenv("PROXY_FORMAT", "ipport"),
        allow_direct=_env_bool("ALLOW_DIRECT", True),
        http_debug=_env_bool("HTTP_DEBUG", False),
        influx_url=os.getenv("INFLUXDB_URL") or None,
        influx_org=os.getenv("INFLUXDB_ORG") or None,
        influx_token=os.getenv("INFLUXDB_ADMIN_TOKEN")
        or os.getenv("INFLUXDB_TOKEN")
        or None,
        influx_bucket=os.getenv("INFLUXDB_BUCKET") or None,
        influx_measurement=os.getenv("INFLUXDB_MEASUREMENT", "tashu_station"),
        influx_weather_measurement=os.getenv(
            "INFLUXDB_MEASUREMENT_WEATHER", "tashu_weather"
        ),
        pb_url=os.getenv("PB_URL") or None,
        pb_admin_token=os.getenv("PB_ADMIN_TOKEN") or None,
        pb_station_collection=os.getenv("PB_STATION_COLLECTION", "station"),
        pb_zone_collection=os.getenv("PB_ZONE_COLLECTION", "zone"),
    )
