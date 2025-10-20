from __future__ import annotations
from typing import Any, Dict, List, Tuple
import os, sys, asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from collector import parking_count as _sync_parking
from .fetch_weather import (
    get_open_weather_response,
    parse_weather_data,
    shutdown_weather_client,
)
from .station import get_zone_by_station_id


async def get_parking_count_response() -> dict:
    return await asyncio.to_thread(_sync_parking.get_parking_count_response)


def parse_parking_count(resp: dict) -> List[Tuple[str, int]]:
    return _sync_parking.parse_parking_count(resp)


async def insert_parking_count(
    rows: List[Tuple[str, int]], weather_by_station: Dict[str, Dict[str, Any]]
) -> None:
    return await asyncio.to_thread(
        _sync_parking.insert_parking_count, rows, weather_by_station
    )


async def collect_and_insert_all() -> None:
    load_dotenv()
    resp = await get_parking_count_response()
    rows = parse_parking_count(resp)
    ow_key = os.getenv("OPENWEATHER_API_KEY")
    sem = asyncio.Semaphore(int(os.getenv("WEATHER_CONCURRENCY", "10")))

    async def fetch_one(station_id: str):
        async with sem:
            zone = await get_zone_by_station_id(station_id)
            weather_json = await get_open_weather_response(
                ow_key, zone["center_lat"], zone["center_lon"]
            )
            return station_id, parse_weather_data(weather_json)

    weather_pairs = await asyncio.gather(*(fetch_one(stid) for stid, _ in rows))
    weather_by_station = dict(weather_pairs)
    await insert_parking_count(rows, weather_by_station)
    await shutdown_weather_client()


if __name__ == "__main__":
    asyncio.run(collect_and_insert_all())
