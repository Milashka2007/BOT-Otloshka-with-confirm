import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent
from dotenv import load_dotenv
from handlers.investor import investor_router
from handlers.post import post_router
from middlewares.db import DataBaseSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.post import load_post
from handlers.ref import ref_router
from work_chinaki.chanel import chanel_router
from work_chinaki.ban import ban_router
import logging

load_dotenv()
from database.engine import create_db, drop_db, session_maker
from handlers.admin_router import admin_router





TOKEN = os.getenv('TOKEN')
if not TOKEN:
    raise ValueError("Токен бота отсутствует. Укажите его в файле .env в переменной TOKEN.")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()


#dp.include_router(admin_router)
#dp.include_router(investor_router)
dp.include_router(post_router)
dp.include_router(chanel_router)
dp.include_router(ban_router)
#dp.include_router(ref_router)



# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


'''async def error_handler(event: ErrorEvent, state: FSMContext):
    """
    Обработчик ошибок: очищает все FSM-контексты и логирует исключение.

    :param event: ErrorEvent с информацией об ошибке.
    :param state: FSM-контекст.
    """
    # Логируем информацию об ошибке
    logger.error(f"Произошла ошибка: {event.exception}")

    # Проверяем, есть ли активное состояние
    if state:
        try:
            await state.clear()  # Очищаем FSM-контекст
            logger.info("FSM-контекст успешно очищен.")
        except Exception as cleanup_error:
            logger.error(f"Ошибка при очистке FSM-контекста: {cleanup_error}")

    # Отправляем пользователю уведомление, если возможно
    if event.update and isinstance(event.update, types.Message):
        try:
            await event.update.answer("Произошла ошибка. Пожалуйста, попробуйте снова.")
        except Exception as notify_error:
            logger.error(f"Не удалось уведомить пользователя об ошибке: {notify_error}")

dp.errors.register(error_handler)'''

async def on_startup(bot):
    await create_db()

    #await drop_db()

async def on_shutdown(bot):
    print('бот ушел за хлебом')

async def main():
    try:
        print("Запуск бота...")
        scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
        scheduler.add_job(load_post, trigger='interval', seconds=60, kwargs = {'bot': bot})
        scheduler.start()
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        dp.update.middleware(DataBaseSession(session_pool=session_maker))
        await bot.delete_webhook(drop_pending_updates=True)

        # Запускаем polling
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        # Закрываем сессию бота
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())