import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from dotenv import load_dotenv
from database.models import Base
load_dotenv()
engine = create_async_engine(os.getenv("DB_LITE"), echo=True)

session_maker=async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)