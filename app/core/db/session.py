from contextlib import asynccontextmanager

from sqlalchemy import NullPool

from app.core.config import settings

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)




engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    connect_args={"ssl": True,}         
)

engine_celery = create_async_engine(settings.DATABASE_URL, echo=True, pool_pre_ping=True, poolclass=NullPool)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

AsyncSessionLocalCelery = async_sessionmaker(
    engine_celery, expire_on_commit=False, autoflush=False, autocommit=False
)



async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            #await session.commit()
        except:
            #await session.rollback()
            raise

@asynccontextmanager
async def get_async_session():
    async with AsyncSessionLocalCelery() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()