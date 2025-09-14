from typing import Iterable, Dict, Any
from datetime import datetime, timezone
from collector.core.base import Scraper
from collector.core.factory import register
from collector.core.types import ParkingCount

@register("parking_count")
class ParkingCountScraper(Scraper):
    def fetch(self) -> Dict[str, Any]:
        return self.client.fetch_all_stations_raw()

    def parse(self, raw: Dict[str, Any]) -> Iterable[dict]:
        ts = datetime.now(timezone.utc).astimezone().isoformat()
        for item in raw.get("results", []):
            pc = item.get("parking_count")
            if pc is None:
                continue
            yield ParkingCount(
                station_id=str(item.get("id")),
                parking_count=int(pc),
                ts=ts,
            ).__dict__
