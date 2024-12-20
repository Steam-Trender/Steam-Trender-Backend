from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.settings import settings

engine: AsyncEngine = create_async_engine(
    settings.get_db_url,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def reset_db():
    async with engine.begin() as conn:

        def reflect_tables(conn):
            meta = MetaData()
            meta.reflect(bind=conn)
            return meta

        meta = await conn.run_sync(reflect_tables)
        for table in reversed(meta.sorted_tables):
            await conn.execute(table.delete())
