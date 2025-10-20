from __future__ import annotations
from typing import Any, Dict, List, Tuple
import os, sys, ssl, asyncio
import aiohttp
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from collector import station as _sync_station

PB_URL = os.getenv("PB_URL", "http://localhost:8090")
TASHU_URL = "https://bikeapp.tashu.or.kr:50041/v1/openapi/station"


def _ssl_context() -> ssl.SSLContext | bool:
    v = os.getenv("VERIFY_SSL", "1").strip()
    if v in ("0", "false", "False", "FALSE", "no"):
        return ssl._create_unverified_context()
    cafile = os.getenv("CA_BUNDLE", "").strip()
    if cafile:
        return ssl.create_default_context(cafile=cafile)
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return True


async def get_station_response(URL: str = TASHU_URL) -> Dict[str, Any]:
    headers = {"api-token": os.getenv("TASHU_KEY")}
    ctx = _ssl_context()
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(URL, headers=headers, ssl=ctx) as res:
            if res.status == 200:
                return await res.json()
            m = {
                400: "토큰이 만료되었거나 잘못되었습니다.",
                404: "페이지를 찾을 수 없습니다.",
                500: "서버 내부 오류가 발생하였습니다.",
            }
            raise RuntimeError(m.get(res.status, f"HTTP {res.status}"))


def parse_station(resp: Dict[str, Any]):
    return _sync_station.parse_station(resp)


async def fetch_all_zones() -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_sync_station.fetch_all_zones)


async def find_zone_id(
    lat: float, lon: float, zones: List[Dict[str, Any]]
) -> str | None:
    return await asyncio.to_thread(_sync_station.find_zone_id, lat, lon, zones)


async def pb_upsert_station(station_row: Dict[str, Any]) -> Dict[str, Any]:
    return await asyncio.to_thread(_sync_station.pb_upsert_station, station_row)


async def insert_station(rows: List[Dict[str, Any]]) -> None:
    return await asyncio.to_thread(_sync_station.insert_station, rows)


async def get_zone_by_station_id(id: str) -> dict[str, Any]:
    return await asyncio.to_thread(_sync_station.get_zone_by_station_id, id)


async def refresh_and_store_stations() -> None:
    load_dotenv()
    resp = await get_station_response()
    rows = parse_station(resp)
    await insert_station(rows)


if __name__ == "__main__":
    asyncio.run(refresh_and_store_stations())
