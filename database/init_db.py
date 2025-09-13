from database.connection import DBObject
from model.base_class import Base
import asyncio

async def create_all():
    await DBObject.init_async_db()
    async with DBObject.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_all())