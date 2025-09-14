from decimal import Decimal
from typing import Iterable, Dict, Any
from collector.core.base import Scraper
from collector.core.factory import register
from collector.core.types import Station

@register("station")
class StationScraper(Scraper):
    def fetch(self) -> Dict[str, Any]:
        # 모든 페이지 병합
        return self.client.fetch_all_stations_raw()

    def parse(self, raw: Dict[str, Any]) -> Iterable[dict]:
        for item in raw.get("results", []):
            yield Station(
                station_id=str(item.get("id")),
                name=item.get("name", ""),
                name_en=item.get("name_en"),
                name_cn=item.get("name_cn"),
                x_pos=Decimal(str(item.get("x_pos"))),
                y_pos=Decimal(str(item.get("y_pos"))),
                address=item.get("address"),
                capacity=int(item.get("parking_count")) if item.get("parking_count") is not None else None,
            ).__dict__
