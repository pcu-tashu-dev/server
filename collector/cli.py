import argparse
import importlib
import pkgutil

from collector.core.client import TashuApiClient
from collector.core.factory import ScraperFactory

def load_scrapers():
    import collector.scrapers as pkg
    for mod in pkgutil.iter_modules(pkg.__path__, pkg.__name__ + "."):
        importlib.import_module(mod.name)

def run_scraper(kind: str, limit: int | None = None):
    load_scrapers()

    client = TashuApiClient()
    scraper = ScraperFactory.create(kind, client=client)
    records = scraper.run()
    if limit is not None:
        records = records[:limit]
    print(f"[{kind}] collected {len(records)} records")
    for r in records:
        print(r)
    return records

def main():
    parser = argparse.ArgumentParser(description="Collector CLI - Tashu API (single endpoint)")
    parser.add_argument(
        "--kind",
        choices=["station", "parking_count"],
        default="station",
        help="실행할 스크레이퍼",
    )
    parser.add_argument("--limit", type=int, default=None, help="출력 레코드 개수 제한")
    args = parser.parse_args()
    run_scraper(args.kind, args.limit)