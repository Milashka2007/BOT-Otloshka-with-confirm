from aiogram import Router, types, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import Command, ChatMemberUpdatedFilter
from aiogram.types import CallbackQuery, ChatMemberUpdated
from datetime import *
from database.orm import orm_ref_exists, orm_add_ref
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from database.engine import session_maker
from buttons.buttons_user import ref_kb
from config import TOKEN, CHANNEL_ID, BOT_USERNAME
from dotenv import load_dotenv
load_dotenv()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

ref_router = Router()

async def make_link(user_id):
    return f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"

@ref_router.message(Command('start'))
async def start_handler(message: types.Message, session: AsyncSession):
    if await orm_ref_exists(session, message.from_user.id):

        await message.answer('Привет! Ты в реф-меню', reply_markup=ref_kb)
    else:
        name = message.from_user.full_name
        await orm_add_ref(session, message.from_user.id, name, 'ref')
        await message.answer('Привет, только что я добавил тебя как реферала!\n'
                             'Тут ты получаешь свою индивидуальную ссылку для привлечения подписчиков.\n'
                             'За 1 привлеченного человека я буду платить тебе 10 рублей!\n'
                             'Максимум в день - 50 человек.\n'
                             'Запросить выплату ты сможешь, если привлечешь 15 и более людей.\n'
                             'Если человек, которого ты привел, отпишется в течении 3 дней, то выплата не будет засчитана.\n'
                             'Также, если после этого он подпишется повторно, то выплата произведена не будет.\n'
                             'Надеюсь на долгое сотрудничество!', reply_markup=ref_kb)

@ref_router.message(F.text=='Получить ссылку')
async def send_link(message: types.Message):
    link = await make_link(message.from_user.id)
    await message.answer(f'Ваша ссылка - {link}')