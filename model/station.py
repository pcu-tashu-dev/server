from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, String, Float
from model.base_class import Base

class Station(Base):
    __tablename__ = "station"
    
    station_id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    name_en = Column(String, nullable=True)
    name_cn = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    address = Column(String, nullable=True)

    raw = Column(JSONB, nullable=True)

    def get_attributes(self) -> dict:
        return {
            "station_id": self.station_id,
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "address": self.address,
            "raw": self.raw
        }