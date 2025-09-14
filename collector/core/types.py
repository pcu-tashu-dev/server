from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass(frozen=True)
class Station:
    station_id: str
    name: str
    name_en: str | None
    name_cn: str | None
    x_pos: Decimal 
    y_pos: Decimal
    address: str | None
    capacity: Optional[int] = None

@dataclass(frozen=True)
class ParkingCount:
    station_id: str
    parking_count: int
    ts: str  # ISO8601 timestamp
