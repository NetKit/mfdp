from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core import settings
from sqlalchemy.orm import sessionmaker

import asyncpg

class Base(DeclarativeBase):
    pass

engine = create_async_engine(f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}/{settings.db_name}", echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def build_asyncpg_conn():
    return await asyncpg.connect(
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        host=settings.db_host,
    )
