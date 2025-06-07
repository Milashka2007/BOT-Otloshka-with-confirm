from aiogram import Router, types, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import Command, ChatMemberUpdatedFilter
from aiogram.types import CallbackQuery, ChatMemberUpdated
from datetime import *

from telebot.apihelper import get_chat

from database.orm import orm_add_user, increment_comment_count, is_user_in_db, delete_user_from_db, \
    orm_get_referrer_by_user_id, orm_increment_referral_count, orm_add_left_user, is_user_in_kicked_db, delete_user_from_kicked_db, orm_add_zhaloba
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from buttons.buttons_user import work_chanel
import os
from database.engine import session_maker
from dotenv import load_dotenv
from config import ADMIN_IDS

load_dotenv()

TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


chanel_router = Router()


'''@chanel_router.message(F.content_type == ContentType.STICKER)'''


@chanel_router.chat_member()
async def on_user_added_to_channel(chat_member_updated: ChatMemberUpdated):
    if chat_member_updated.new_chat_member.status == "member":
        async with session_maker() as session:
            if not (await is_user_in_kicked_db(session, chat_member_updated.new_chat_member.user.id)):
                user_id = chat_member_updated.new_chat_member.user.id
                full_name = chat_member_updated.new_chat_member.user.full_name
                await orm_add_user(session, user_id, full_name)
            else:
                user_id = chat_member_updated.new_chat_member.user.id
                full_name = chat_member_updated.new_chat_member.user.full_name
                await delete_user_from_kicked_db(session, user_id)
                await orm_add_user(session, user_id, full_name)

    if chat_member_updated.new_chat_member.status == "left":
        async with session_maker() as session:
            user_id = chat_member_updated.old_chat_member.user.id
            await orm_add_left_user(session, user_id, chat_member_updated.new_chat_member.user.full_name, 'left')
            await delete_user_from_db(session, user_id)

    if chat_member_updated.new_chat_member.status == "kicked":
        async with session_maker() as session:
            user_id = chat_member_updated.old_chat_member.user.id
            await orm_add_left_user(session, user_id, chat_member_updated.new_chat_member.user.full_name, 'kicked')
            await delete_user_from_db(session, user_id)



@chanel_router.message(F.reply_to_message != None)
async def comment_message_handler(message: types.Message):
    # Проверяем, что сообщение является ответом на сообщение
    # Добавляем 1 к счетчику сообщений в комментариях для пользователя в базе данных
    async with session_maker() as session:
        #if is_user_in_db(session, message.from_user.id):
            await increment_comment_count(session, message.from_user.id)

            if message.reply_to_message.text and '@admin' in message.text:
                message_link = f"https://t.me/{message.chat.username}/{message.reply_to_message.message_id}"
                reply= message.reply_to_message
                id2 = message.from_user.id
                chat2 = await bot.get_chat(id2)
                zhaloba_ot = '@'+chat2.username
                id = reply.from_user.id
                chat = await bot.get_chat(id)
                zhaloba_na = '@'+chat.username
                await orm_add_zhaloba(session, message_link, zhaloba_ot, zhaloba_na)
                await bot.send_message(ADMIN_IDS[0], 'Появилась новая жалоба!')
                await message.reply(f"Жалоба на {zhaloba_na} была отправлена нашим модераторам!", parse_mode=ParseMode.HTML)


@chanel_router.message(F.text=='Работа с каналом')
async def work_main(message: types.Message):
    await message.answer('Что делаем?', reply_markup = work_chanel)









