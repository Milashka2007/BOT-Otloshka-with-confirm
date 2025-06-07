from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm import orm_get_zhaloba_by_id
from config import ADMIN_IDS

confirm_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Подтвердить ✅"), KeyboardButton(text="Отменить ❌")]
    ],
    resize_keyboard=True,
    input_field_placeholder='Чем могу быть полезен?')

async def start_post(message: types.Message):
    keyboard = [
        [KeyboardButton(text='Сделать пост'), KeyboardButton(text='Рефералка')],
        [KeyboardButton(text='Работа с каналом'), KeyboardButton(text='Посмотреть посты')]
    ]

    if message.from_user.id in ADMIN_IDS:
        keyboard.append([KeyboardButton(text="Новые посты"), KeyboardButton(text='Изменить/Подтвердить пост')])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


post_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Подтвердить пост✅"), KeyboardButton(text="Отменить пост❌")],
        [KeyboardButton(text="Самому изменить пост⚙️"), KeyboardButton(text="Отправить комментарий⚙️")]
    ],
    resize_keyboard=True,
    input_field_placeholder='Чем могу быть полезен?')

otpravit_post = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ДА ✅"), KeyboardButton(text="Нет ❌"), KeyboardButton(text='Изменить текст⚙️')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Чем могу быть полезен?')

da_net_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ДА ✅"), KeyboardButton(text="Нет ❌")]
    ],
    resize_keyboard=True,
    input_field_placeholder='Чем могу быть полезен?')


async def referalka(message: types.Message):
    keyboard = [
        [KeyboardButton(text='Узнать выплаты'), KeyboardButton(text='Сделать выплату')],
        [KeyboardButton(text='Все рефералы')]
    ]

    if message.from_user.id in ADMIN_IDS:
        keyboard.append([KeyboardButton(text="Добавить админа")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


ref_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Получить ссылку')],
        [KeyboardButton(text='Приведено всего'), KeyboardButton(text='Приведено сегодня')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Чем могу быть полезен?')

work_chanel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Посмотреть жалобы'), KeyboardButton(text='Администрация')]
    ]
)


async def zhaloba_kbds(session: AsyncSession, id):
    zhaloba = await orm_get_zhaloba_by_id(session, id)
    for i in zhaloba:
        zhaloba_kb = InlineKeyboardBuilder()
        zhaloba_kb.add(InlineKeyboardButton(text='Виновен', callback_data=f'Виновен'))
        zhaloba_kb.add(InlineKeyboardButton(text='Не виновен', callback_data=f'Не виновен'))
        zhaloba_kb.add(InlineKeyboardButton(text='Забанить сразу', callback_data=f'Забанить сразу'))
    return zhaloba_kb.as_markup()

