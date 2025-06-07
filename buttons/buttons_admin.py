from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm import orm_get_all_products_kbds, orm_get_investors

admin_kb=ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Продажи'), KeyboardButton(text='Расходы')],
            [KeyboardButton(text='Выплаты'), KeyboardButton(text='Прибыль')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Чем могу быть полезен?')


type_kb=ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Товар'), KeyboardButton(text='Доставка'), KeyboardButton(text='Другое')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Чем могу быть полезен?')

def yes_no():
    yes_no = InlineKeyboardBuilder()
    yes_no.add(InlineKeyboardButton(text='Подтвердить', callback_data='yes'))
    yes_no.add(InlineKeyboardButton(text='Отменить', callback_data='no'))
    return yes_no.as_markup()

rashody_kb=ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Добавить расходы'), KeyboardButton(text='Расходы за месяц'), KeyboardButton(text='В меню')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Чем могу быть полезен?')

prodazhi_kb=ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Добавить продажу'), KeyboardButton(text='Продажи за месяц')],
        [KeyboardButton(text='Добавить товар'), KeyboardButton(text='В меню')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Чем могу быть полезен?')

async def products_kbds(session: AsyncSession):
    product_kb = InlineKeyboardBuilder()
    products = await orm_get_all_products_kbds(session)
    row = []
    for i in products:
        row.append(InlineKeyboardButton(text=f'{i.name}', callback_data=f'{i.name}'))
        if len(row) == 3:
            product_kb.row(*row)
            row = []
    if row:
        product_kb.row(*row)
    return product_kb.as_markup()

income_kb=ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Прибыль за месяц'), KeyboardButton(text='Суммарная прибль')],
        [KeyboardButton(text='В меню')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Чем могу быть полезен?')

vyplaty_kb=ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Узнать выплаты'), KeyboardButton(text='Добавить инвестора')],
        [KeyboardButton(text='Cделать выплату'), KeyboardButton(text='Удалить инвестора')],
        [KeyboardButton(text='В меню')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Чем могу быть полезен?')


async def investor_kbds(session: AsyncSession):
    product_kb = InlineKeyboardBuilder()
    products = await orm_get_investors(session)
    row = []
    for i in products:
        row.append(InlineKeyboardButton(text=f'{i.name}', callback_data=f'{i.name}'))
        if len(row) == 3:
            product_kb.row(*row)
            row = []
    if row:
        product_kb.row(*row)
    return product_kb.as_markup()