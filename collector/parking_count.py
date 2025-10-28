# parking_count.py
from __future__ import annotations
import json, asyncio
from typing import Dict, Any, List, Tuple
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from settings import Settings, load_settings
from http_client import AsyncHTTP


async def get_parking_count_response(http: AsyncHTTP, st: Settings) -> Dict[str, Any]:
    return await http.get_json(
        st.tashu_url,
        headers={"api-token": st.tashu_key},
        max_attempts=st.retry_total + 1,
    )


def parse_parking_count(res: Dict[str, Any]) -> List[Tuple[str, int]]:
    data = res.get("results") or res.get("result") or res.get("data") or []
    out: List[Tuple[str, int]] = []
    for x in data:
        sid = str(x.get("id") or x.get("station_id") or x.get("stationId") or "")
        pc = x.get("parking_count") or x.get("parkingCount") or x.get("parking") or 0
        if sid:
            out.append((sid, int(pc)))
    return out


async def _get_zone_by_station_id(
    http: AsyncHTTP, st: Settings, sid: str
) -> Dict[str, Any]:
    if not st.pb_url:
        return {}
    url = f"{st.pb_url.rstrip('/')}/stations/{sid}"
    r = await http.get_json(
        url,
        headers={"Content-Type": "application/json"},
        max_attempts=st.retry_total + 1,
    )
    if isinstance(r, dict) and r.get("success") is False:
        return {}
    return r.get("zone") or {}


async def _get_weather(
    http: AsyncHTTP, st: Settings, lat: float, lon: float
) -> Dict[str, Any]:
    if not st.openweather_api_key:
        return {}
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": st.openweather_api_key,
        "units": "metric",
        "lang": "kr",
    }
    return await http.get_json(url, params=params, max_attempts=st.retry_total + 1)


def _parse_weather(d: Dict[str, Any]) -> Dict[str, Any]:
    w = d.get("weather") or []
    m = d.get("main") or {}
    wd = d.get("wind") or {}
    return {
        "weather": [x.get("main") for x in w],
        "temp": m.get("temp"),
        "wind_speed": wd.get("speed"),
    }


async def _augment_with_weather(
    http: AsyncHTTP, st: Settings, rows: List[Tuple[str, int]]
) -> Dict[str, Dict[str, Any]]:
    if not (st.pb_url and st.openweather_api_key):
        return {}
    sem = asyncio.Semaphore(st.concurrency)

    async def one(sid: str) -> Tuple[str, Dict[str, Any]]:
        async with sem:
            z = await _get_zone_by_station_id(http, st, sid)
            lat = z.get("center_lat")
            lon = z.get("center_lon")
            if lat is None or lon is None:
                return sid, {}
            d = await _get_weather(http, st, float(lat), float(lon))
            return sid, _parse_weather(d)

    pairs = await asyncio.gather(*(one(s) for s, _ in rows))
    return dict(pairs)


def _write_influx(
    st: Settings, rows: List[Tuple[str, int]], wx: Dict[str, Dict[str, Any]]
) -> None:
    if not (st.influx_url and st.influx_org and st.influx_token and st.influx_bucket):
        return
    c = InfluxDBClient(
        url=st.influx_url,
        org=st.influx_org,
        token=st.influx_token,
        bucket=st.influx_bucket,
    )
    w = c.write_api(write_options=SYNCHRONOUS)
    measurement = "tashu_station"
    pts = []
    for sid, cnt in rows:
        wd = wx.get(sid) or {}
        p = (
            Point(measurement)
            .tag("station_id", str(sid))
            .tag("weather_main", str(wd.get("weather") or ""))
        )
        p = p.field("parking_count", int(cnt))
        if wd.get("temp") is not None:
            p = p.field("temp", float(wd["temp"]))
        if wd.get("wind_speed") is not None:
            p = p.field("wind_speed", float(wd["wind_speed"]))
        pts.append(p)
    if pts:
        w.write(bucket=st.influx_bucket, org=st.influx_org, record=pts)
    c.close()


async def insert_parking_count(rows: List[Tuple[str, int]], st: Settings) -> None:
    http = AsyncHTTP(st)
    try:
        wx = await _augment_with_weather(http, st, rows)
        await asyncio.to_thread(_write_influx, st, rows, wx)
    finally:
        await http.close()


async def main() -> None:
    st = load_settings()
    http = AsyncHTTP(st)
    try:
        raw = await get_parking_count_response(http, st)
        rows = parse_parking_count(raw)
    finally:
        await http.close()
    await insert_parking_count(rows, st)
    print(json.dumps({"count": len(rows), "sample": rows[:3]}, ensure_ascii=False))
