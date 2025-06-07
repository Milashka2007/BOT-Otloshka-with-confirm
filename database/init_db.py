from database.engine import create_db, session_maker
from database.models import Base
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

async def init_database():
    # Создаем базу данных
    await create_db()
    
    # Здесь можно добавить начальные данные, если они нужны
    async with session_maker() as session:
        # Пример добавления начальных данных
        # await add_initial_data(session)
        pass

if __name__ == "__main__":
    asyncio.run(init_database()) 