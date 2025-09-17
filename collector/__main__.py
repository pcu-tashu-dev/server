from collector.core.loader import autodiscover_scrapers
from collector.core.factory import ScraperFactory
from database.sinks import sink_influx_generic
import argparse, os, asyncio, logging, inspect
from collector.core.client import TashuApiClient
from database.connection import DBObject
from dotenv import load_dotenv

log = logging.getLogger(__name__)

async def _maybe_await(value):
    return await value if inspect.isawaitable(value) else value

async def run() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", required=True)
    parser.add_argument("--sink", choices=["none", "influx"], default=None)
    parser.add_argument("--bucket", default=None)
    parser.add_argument("--measurement", default=None)
    parser.add_argument("--tag-keys", default="station_id")
    parser.add_argument("--time-key", default=None)
    parser.add_argument("--batch-size", type=int, default=5000)
    args = parser.parse_args()

    sink = args.sink
    if sink is None:
        sink = "influx" if os.getenv("INFLUX_URL") else "none"

    autodiscover_scrapers()

    api_client = TashuApiClient.from_env()
    scraper = ScraperFactory.create(args.kind, client=api_client)

    raw = await _maybe_await(scraper.fetch())
    items_iter = await _maybe_await(scraper.parse(raw))
    items = list(items_iter) if not isinstance(items_iter, list) else items_iter

    if sink == "none":
        print(f"[dry-run] parsed={len(items)}")
        return 0

    if sink == "influx":
        await DBObject.init("influx")
        measurement = args.measurement or args.kind
        bucket = args.bucket or os.getenv("INFLUX_BUCKET")
        if not bucket:
            raise SystemExit("Influx bucket이 지정되지 않았습니다.")
        tag_keys = tuple(k.strip() for k in args.tag_keys.split(",") if k.strip())
        wrote = await sink_influx_generic(
            items,
            measurement=measurement,
            bucket=bucket,
            tag_keys=tag_keys,
            time_key=args.time_key,
            batch_size=args.batch_size,
        )
        print(f"[influx] measurement={measurement} wrote={wrote} points to bucket={bucket}")
        return 0

    raise SystemExit(f"unknown sink: {sink}")

def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()