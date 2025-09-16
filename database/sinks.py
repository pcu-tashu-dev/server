from database.connection import DBObject, InfluxDBConnector
from typing import Iterable, Sequence, Optional, List, Any
from decimal import Decimal
import influxdb_client
import datetime as dt
import logging

log = logging.getLogger(__name__)

def _to_number(v: Any):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, Decimal):
        return float(v)
    try:
        fv = float(v)
        return int(fv) if isinstance(fv, float) and fv.is_integer() else fv
    except Exception:
        return None

def _to_bool(v: Any):
    if isinstance(v, bool):
        return v
    return None

def _parse_time(val: Any) -> Optional[dt.datetime]:
    if val is None:
        return None
    if isinstance(val, (int, float)) or (isinstance(val, str) and val.isdigit()):
        x = int(val)
        if x > 10000000000:
            return dt.datetime.fromtimestamp(x / 1000, tz=dt.timezone.utc)
        return dt.datetime.fromtimestamp(x, tz=dt.timezone.utc)
    if isinstance(val, str):
        s = val.strip()
        if s.endswith("Z"):
            s = s.replace("Z", "+00:00")
        try:
            t = dt.datetime.fromisoformat(s)
            return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)
        except Exception:
            return None
    return None

def _build_point(measurement: str, item: dict, tag_keys: Sequence[str], time_key: Optional[str]):
    if influxdb_client is None:
        raise RuntimeError("influxdb-client가 설치되지 않았습니다.")
    p = influxdb_client.Point(measurement)
    for k in tag_keys:
        if k in item and item[k] is not None:
            p.tag(k, str(item[k]))
    if time_key and time_key in item:
        t = _parse_time(item[time_key])
        if t is not None:
            p.time(t)
    skip = set(tag_keys) | ({time_key} if time_key else set())
    for k, v in item.items():
        if k in skip or v is None:
            continue
        b = _to_bool(v)
        if b is not None:
            p.field(k, b)
            continue
        num = _to_number(v)
        if num is not None:
            p.field(k, num)
            continue
        p.field(k, str(v))
    return p

async def sink_influx_generic(items: Iterable[dict], *, measurement: str, bucket: Optional[str], tag_keys: Sequence[str] = ("station_id",), time_key: Optional[str] = None, batch_size: int = 5000) -> int:
    conn = DBObject.get_connector()
    if not isinstance(conn, InfluxDBConnector):
        raise RuntimeError("현재 DB 드라이버는 InfluxDB가 아닙니다.")
    wrote = 0
    batch: List["influxdb_client.Point"] = []
    for it in items:
        try:
            p = _build_point(measurement, it, tag_keys, time_key)
            if p is None:
                continue
            batch.append(p)
            if len(batch) >= batch_size:
                await conn.write(batch, bucket=bucket)
                wrote += len(batch)
                batch.clear()
        except Exception:
            continue
    if batch:
        await conn.write(batch, bucket=bucket)
        wrote += len(batch)
    return wrote
