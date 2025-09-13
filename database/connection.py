from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import urllib.parse
import os
import logging
from dotenv import load_dotenv

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

class DBObject:
    engine = None
    async_session = None

    @staticmethod
    async def init_async_db():
        load_dotenv()

        db_config = {
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "name": os.getenv("DB_NAME"),
        }

        if None in db_config.values():
            missing = [k for k, v in db_config.items() if v is None]
            raise RuntimeError(f"환경 변수 누락: {', '.join(missing)}. .env 파일을 확인하세요.")

        db_url = (
            f"postgresql+asyncpg://{urllib.parse.quote_plus(db_config['user'])}:"
            f"{urllib.parse.quote_plus(db_config['password'])}@{db_config['host']}:{db_config['port']}/"
            f"{urllib.parse.quote_plus(db_config['name'])}"
        )

        try:
            DBObject.engine = create_async_engine(db_url, echo=True)
            DBObject.async_session = async_sessionmaker(
                bind=DBObject.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        except Exception as e:
            logging.error(f"데이터베이스 연결 오류: {e}")
            raise RuntimeError("데이터베이스 연결에 실패했습니다.") from e

    @staticmethod
    async def get_db():
        if DBObject.async_session is None:
            raise RuntimeError("DB 초기화되지 않음. init_async_db()를 먼저 호출하세요.")
        async with DBObject.async_session() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                print(f"Error: {e}")
                await session.rollback()
                raise e