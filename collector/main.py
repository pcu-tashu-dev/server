# main.py
from __future__ import annotations
import sys, json, asyncio
from settings import load_settings
import os, fcntl


def _acquire_lock(name: str):
  """
  Prevent overlapping runs per target (e.g., parking_count).
  If another process holds the lock, exit silently.
  """
  lock_path = f"/tmp/tashu_dev_{name}.lock"
  fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
  try:
    fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
  except OSError:
    raise SystemExit(f"Another {name} job is already running")
  os.write(fd, str(os.getpid()).encode("utf-8"))
  return fd
from http_client import AsyncHTTP
from station import get_station_response, parse_station, insert_station
from parking_count import (
    get_parking_count_response,
    parse_parking_count,
    insert_parking_count,
)
from forecast_predict import predict_and_store_for_stations


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
        # 혹시 모를 중복 id 제거 (최신 값 우선), sid 정규화는 parse에서 upper/strip 처리
        dedup = {}
        for sid, cnt in rows:
            dedup[sid] = cnt
        rows = list(dedup.items())
        await insert_parking_count(rows, st)
        await predict_and_store_for_stations(rows, st)
        print(json.dumps({"count": len(rows), "sample": rows[:3]}, ensure_ascii=False))
    finally:
        await http.close()


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "station"
    lock_fd = _acquire_lock(target)
    if target == "station":
        asyncio.run(run_station())
    elif target == "parking_count":
        asyncio.run(run_parking())
    else:
        raise SystemExit("station | parking_count")
    # keep lock fd open until process exit to hold lock
