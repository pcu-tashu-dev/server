from database.connection import DBFactory
from model.base_class import Base
from model.station import Station
import asyncio

async def create_all():
    postgres_connector = await DBFactory.create(driver="postgres")
    async with postgres_connector.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_all())