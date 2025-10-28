# main.py
from __future__ import annotations
import sys, json, asyncio
from settings import load_settings
from http_client import AsyncHTTP
from station import get_station_response, parse_station, insert_station
from parking_count import (
    get_parking_count_response,
    parse_parking_count,
    insert_parking_count,
)


async def run_station():
    st = load_settings()
    http = AsyncHTTP(st)
    try:
        raw = await get_station_response(http, st)
        rows = parse_station(raw)
        await insert_station(rows, st)
        print(json.dumps({"count": len(rows), "sample": rows[:3]}, ensure_ascii=False))
    finally:
        await http.close()


async def run_parking():
    st = load_settings()
    http = AsyncHTTP(st)
    try:
        raw = await get_parking_count_response(http, st)
        rows = parse_parking_count(raw)
        await insert_parking_count(rows, st)
        print(json.dumps({"count": len(rows), "sample": rows[:3]}, ensure_ascii=False))
    finally:
        await http.close()


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "station"
    if target == "station":
        asyncio.run(run_station())
    elif target == "parking_count":
        asyncio.run(run_parking())
    else:
        raise SystemExit("station | parking_count")
