from database.connection import DBObject, DBFactory
from collector.core.factory import ScraperFactory
from collector.core.client import TashuApiClient
from typing import List, Dict, Any, Optional
import collector.scrapers as scrapers_pkg
from model.station import Station
from influxdb_client import Point
import importlib
import argparse
import asyncio
import pkgutil
import decimal


def load_scrapers() -> None:
    for mod in pkgutil.iter_modules(scrapers_pkg.__path__, scrapers_pkg.__name__ + "."):
        importlib.import_module(mod.name)

def _normalize(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _normalize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalize(v) for v in obj]
    if isinstance(obj, decimal.Decimal):
        return float(obj) if obj % 1 else int(obj)
    return obj


def _sanitize_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [_normalize(r) for r in rows]

async def _save_stations(rows: List[Dict[str, Any]]) -> None:
    await DBObject.init("postgres")
    async for s in DBObject.get_db_session():
        for r in rows:
            st = Station(
                station_id=r.get("station_id") or r.get("id") or r.get("stationId"),
                name=r.get("name") or r.get("station_name"),
                address=r.get("address") or r.get("addr"),
                raw=r,
            )
            if st.station_id is None:
                continue
            s.add(st)
        await s.commit()


async def _write_parking_counts(rows: List[Dict[str, Any]], bucket: Optional[str]) -> None:
    influx = await DBFactory.create("influx")
    points: List[Point] = []
    for r in rows:
        station_id = r.get("station_id") or r.get("stationId") or r.get("id")
        count = r.get("count") or r.get("parking_count") or r.get("available")
        updated_at = r.get("updated_at") or r.get("updatedAt") or r.get("time") or r.get("timestamp")
        if station_id is None or count is None or updated_at is None:
            continue
        p = (
            Point("parking_count")
            .tag("station_id", str(station_id))
            .field("count", int(count))
            .time(updated_at)
        )
        points.append(p)
    if points:
        await influx.write(points, bucket=bucket)

async def _amain(args: argparse.Namespace) -> None:
    load_scrapers()

    client = TashuApiClient()
    scraper = ScraperFactory.create(args.kind, client=client)
    rows = scraper.run()

    rows = _sanitize_rows(rows)

    if args.limit:
        rows = rows[:args.limit]

    if args.kind == "station" and args.sink == "postgres":
        await _save_stations(rows)
        print(f"[station] saved {len(rows)} rows to Postgres")
    elif args.kind == "parking_count" and args.sink == "influx":
        await _write_parking_counts(rows, bucket=args.bucket)
        print(f"[parking_count] wrote {len(rows)} points to Influx")
    else:
        print("invalid combination. use: station→postgres, parking_count→influx")


def main() -> None:
    ap = argparse.ArgumentParser(description="Tashu Collector CLI (server + collector.scrapers, sanitized)")
    ap.add_argument("--kind", choices=["station", "parking_count"], default="station")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--sink", choices=["postgres", "influx"], required=True)
    ap.add_argument("--bucket", default=None)
    args = ap.parse_args()
    asyncio.run(_amain(args))


if __name__ == "__main__":
    main()
