from collector.core.factory import register
from collector.core.base import Scraper
from typing import Iterable, Dict, Any
from decimal import Decimal

@register("station")
class StationScraper(Scraper):
    def __init__(self, client, **kwargs):
        super().__init__(client=client, **kwargs)
        if client is None or not hasattr(client, "fetch_all_stations_raw"):
            raise RuntimeError("StationScraper에는 'fetch_all_stations_raw'를 가진 client가 필요합니다.")

    def fetch(self) -> Dict[str, Any]:
        return self.client.fetch_all_stations_raw()

    def parse(self, raw: Dict[str, Any]) -> Iterable[dict]:
        for item in raw.get("results", []):
            yield {
                "station_id": str(item.get("id")),
                "name": item.get("name", ""),
                "name_en": item.get("name_en"),
                "name_cn": item.get("name_cn"),
                "x_pos": Decimal(str(item.get("x_pos"))),
                "y_pos": Decimal(str(item.get("y_pos"))),
                "address": item.get("address"),
                "capacity": int(item["parking_count"]) if item.get("parking_count") is not None else None,
            }
