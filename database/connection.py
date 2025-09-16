from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncIterator, Optional, Literal, Any, Dict
from influxdb_client.client.write_api import SYNCHRONOUS
from sqlalchemy.exc import SQLAlchemyError
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import influxdb_client
import urllib.parse
import logging
import asyncio
import os



logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    @abstractmethod
    async def init(self) -> None:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    @abstractmethod
    async def ping(self) -> bool:
        ...

class PostgresConnector(BaseConnector):
    def __init__(self, *, user: str, password: str, host: str, port: str, dbname: str, echo: bool = False):
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._dbname = dbname
        self._echo = echo

        self.engine = None
        self.async_session: Optional[async_sessionmaker[AsyncSession]] = None

    def _url(self) -> str:
        return (
            f"postgresql+asyncpg://{urllib.parse.quote_plus(self._user)}:"
            f"{urllib.parse.quote_plus(self._password)}@{self._host}:{self._port}/"
            f"{urllib.parse.quote_plus(self._dbname)}"
        )

    async def init(self) -> None:
        try:
            self.engine = create_async_engine(self._url(), echo=self._echo)
            self.async_session = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)
            async with self.engine.begin() as conn:
                await conn.run_sync(lambda conn: None)
        except Exception as e:
            logger.exception("PostgreSQL 연결 실패")
            raise RuntimeError("PostgreSQL 연결에 실패했습니다.") from e

    async def close(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()

    async def ping(self) -> bool:
        if self.engine is None:
            return False
        try:
            async with self.engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    async def get_session(self) -> AsyncIterator[AsyncSession]:
        if self.async_session is None:
            raise RuntimeError("PostgreSQL 커넥터가 초기화되지 않았습니다.")
        async with self.async_session() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                await session.rollback()
                raise e


class InfluxDBConnector(BaseConnector):
    def __init__(self, *, url: str, token: str, org: str, default_bucket: Optional[str] = None):
        if influxdb_client is None:
            raise RuntimeError("influxdb-client가 설치되어 있지 않습니다. `pip install influxdb-client`")
        self._url = url
        self._token = token
        self._org = org
        self._bucket = default_bucket

        self.client: Optional[influxdb_client.InfluxDBClient] = None
        self._query_api = None
        self._write_api = None

    async def init(self) -> None:
        try:
            self.client = influxdb_client.InfluxDBClient(url=self._url, token=self._token, org=self._org, timeout=30_000)
            self._query_api = self.client.query_api()
            self._write_api = self.client.write_api(write_options=SYNCHRONOUS)
            if not await self.ping():
                raise RuntimeError("InfluxDB ping 실패")
        except Exception as e:
            logger.exception("InfluxDB 연결 실패")
            raise RuntimeError("InfluxDB 연결에 실패했습니다.") from e

    async def close(self) -> None:
        if self.client is not None:
            await asyncio.to_thread(self.client.close)

    async def ping(self) -> bool:
        if self.client is None:
            return False
        try:
            return await asyncio.to_thread(self.client.ping)
        except Exception:
            return False

    async def query(self, flux: str) -> Any:
        if self._query_api is None:
            raise RuntimeError("InfluxDB 커넥터가 초기화되지 않았습니다.")
        return await asyncio.to_thread(self._query_api.query, query=flux, org=self._org)

    async def write(
        self,
        records: Any,
        bucket: Optional[str] = None,
        org: Optional[str] = None,
        write_precision: Optional[str] = None,
    ) -> None:
        if self._write_api is None:
            raise RuntimeError("InfluxDB 커넥터가 초기화되지 않았습니다.")
        bkt = bucket or self._bucket
        if not bkt:
            raise ValueError("bucket이 지정되지 않았습니다. (기본 bucket을 생성자에서 주입하거나 매개변수로 전달하세요)")
        await asyncio.to_thread(
            self._write_api.write, bkt, org or self._org, record=records, write_precision=write_precision
        )

Driver = Literal["postgres", "influx"]

class DBFactory:
    @staticmethod
    async def create(driver: Driver) -> BaseConnector:
        load_dotenv()

        if driver == "postgres":
            cfg = {
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "host": os.getenv("DB_HOST"),
                "port": os.getenv("DB_PORT"),
                "dbname": os.getenv("DB_NAME"),
            }
            missing = [k for k, v in cfg.items() if not v]
            if missing:
                raise RuntimeError(f"환경 변수 누락(Postgres): {', '.join(missing)}")

            connector = PostgresConnector(
                user=cfg["user"],
                password=cfg["password"],
                host=cfg["host"],
                port=cfg["port"],
                dbname=cfg["dbname"],
                echo=True,
            )
            await connector.init()
            return connector

        elif driver == "influx":
            cfg = {
                "url": os.getenv("INFLUX_URL"),
                "token": os.getenv("INFLUX_TOKEN"),
                "org": os.getenv("INFLUX_ORG"),
                "bucket": os.getenv("INFLUX_BUCKET"),
            }
            missing = [k for k, v in cfg.items() if k != "bucket" and not v]
            if missing:
                raise RuntimeError(f"환경 변수 누락(Influx): {', '.join(missing)}")

            connector = InfluxDBConnector(
                url=cfg["url"],
                token=cfg["token"],
                org=cfg["org"],
                default_bucket=cfg["bucket"],
            )
            await connector.init()
            return connector

        else:
            raise ValueError(f"알 수 없는 드라이버: {driver}")

class DBObject:
    _connector: Optional[BaseConnector] = None

    @staticmethod
    async def init(driver: Driver) -> None:
        DBObject._connector = await DBFactory.create(driver)

    @staticmethod
    def get_connector() -> BaseConnector:
        if DBObject._connector is None:
            raise RuntimeError("DB가 초기화되지 않았습니다. DBObject.init(driver)를 먼저 호출하세요.")
        return DBObject._connector
    
    @staticmethod
    async def get_db_session() -> AsyncIterator[AsyncSession]:
        conn = DBObject.get_connector()
        if not isinstance(conn, PostgresConnector):
            raise RuntimeError("현재 드라이버가 PostgreSQL이 아닙니다.")
        async for session in conn.get_session():
            yield session
