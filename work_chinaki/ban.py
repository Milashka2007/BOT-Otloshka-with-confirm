from aiogram import Router, types, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import Command, ChatMemberUpdatedFilter
from aiogram.types import CallbackQuery, ChatMemberUpdated
from datetime import *
from database.orm import orm_add_user, increment_comment_count, is_user_in_db, delete_user_from_db, \
    orm_get_referrer_by_user_id, orm_increment_referral_count, orm_get_admins
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from buttons.buttons_user import work_chanel
import os
from database.engine import session_maker
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


ban_router = Router()
ban_router.message.filter(F.chat_type.contains('supergroup'))

async def get_admins_from_db():
    async with session_maker() as session:
        admin = await orm_get_admins(session)
        admins = []
        for i in admin:
            admins.append(i.user_id)
    print(admins)
    return admins


@ban_router.message(Command('ban'))
async def make_ban(message: types.Message):
    x=0
