from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from datetime import *

from sqlalchemy.ext.asyncio import AsyncSession

from buttons.buttons_admin import admin_kb, type_kb, yes_no, rashody_kb, prodazhi_kb, products_kbds, income_kb, vyplaty_kb
from buttons.calendar import calendar_month, calendar_day
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from database.orm import orm_add_buy, orm_get_expenses_by_month, orm_add_product, orm_get_all_products_kbds, \
    orm_add_sell, orm_get_sell_by_month
from handlers.proc import month_income, all_income
from config import ADMIN_IDS

admin_router = Router()

class Add_expense(StatesGroup):
    type_expense= State()
    price = State()
    day = State()
    month = State()
    date = State()
    check = State()


@admin_router.message(Command('admin'))
async def start(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer('Дарова, босс!', reply_markup=admin_kb)


@admin_router.message(F.text=='В меню')
async def main(message: types.Message):
    await message.answer('Это меню админа', reply_markup=admin_kb)


@admin_router.message(F.text=='Расходы')
async def sell(message: types.Message):
    await message.answer('Что хотите сделать?', reply_markup=rashody_kb)


# rashody za month

@admin_router.message(F.text=='Расходы за месяц')
async def rashody_month(message: types.Message, session: AsyncSession):
    summa=0
    msg=f'Расходы за текущий месяц:\n'
    count=1
    for i in await orm_get_expenses_by_month(session, datetime.now().year, datetime.now().month):
        msg+=f'{count}. {i.type} - {i.price} рублей\n'
        summa+=i.price
        count+=1
    msg+=f'Суммарные расходы в этом месяце состивили {summa} рублей'
    await message.answer(msg, reply_markup=admin_kb)


# add rashody

@admin_router.message(F.text=='Добавить расходы')
async def add_sell(message: types.Message, state: FSMContext):
    await message.answer('Какие расходы?', reply_markup=type_kb)
    await state.set_state(Add_expense.type_expense)


@admin_router.message(Add_expense.type_expense, F.text)
async def type_expense(message: types.Message, state: FSMContext):
    await state.update_data(type_expense=message.text)
    await message.answer('Отлично, сколько это стоило?', reply_markup=ReplyKeyboardRemove())
    await state.set_state(Add_expense.price)


@admin_router.message(Add_expense.price, F.text)
async def price(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await message.answer('Отлично, а теперь скажи мне дату заказа', reply_markup= await calendar_month())
        await state.update_data(price=int(message.text))
        await state.set_state(Add_expense.month)
    else:
        await message.answer('Цена-это число, введи заново')
        await state.set_state(Add_expense.price)

# calendar

@admin_router.callback_query(F.data=='year')
async def calendaric_year(callback: CallbackQuery):
    current_year = str(datetime.now().year)
    await callback.answer(f'Текущий год-{current_year}')

@admin_router.callback_query(F.data=='weekday')
@admin_router.callback_query(F.data=='month')
async def calendaric_month(callback: CallbackQuery, state: FSMContext):
    meet=await state.get_data()
    month = meet['month']
    await callback.answer(f'Текущий месяц-{month}')


@admin_router.callback_query(Add_expense.month)
async def calendaric_month(callback: CallbackQuery, state: FSMContext):
    month=callback.data
    await state.update_data(month=month)
    await callback.message.edit_text('Выберите дату', reply_markup=await calendar_day(month))
    await state.set_state(Add_expense.day)


@admin_router.callback_query(Add_expense.day)
async def calendaric_day(callback: CallbackQuery, state: FSMContext):
    day=callback.data
    if day=='назад':
        await callback.message.edit_text('Выберите месяц', reply_markup=await calendar_month())
        await state.set_state(Add_expense.month)
    else:
        await state.update_data(day=day)
        meet = await state.get_data()
        month = meet['month']
        day = meet['day']
        if int(day) < 10:
            day = '0' + day
        months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
                  'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
        month = str(months.index(month) + 1)
        if int(month) < 10:
            month = '0' + month
        date = str(datetime.now().year) + '.' + month + '.' + day
        await state.update_data(date=date)
        await callback.message.delete()
        res = await state.get_data()
        await callback.message.answer(
            f'Тип расхода: {res['type_expense']}\n'
            f'Цена: {res['price']}\n'
            f'Дата: {res['date']}\n',
            reply_markup=yes_no()
        )
        await state.set_state(Add_expense.check)


@admin_router.callback_query(Add_expense.check, F.data)
async def ask(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.delete()
    res = await state.get_data()
    if callback.data == 'yes':
        await orm_add_buy(session, res)
        await callback.message.answer(f'Отлично, записал.\n'
            f'Тип расхода: {res['type_expense']}\n'
            f'Цена: {res['price']}\n'
            f'Дата: {res['date']}\n',
            reply_markup=admin_kb
        )
        await state.clear()
    else:
        await callback.message.answer(f'Отлично, отменил.\n'
            f'Тип расхода: {res['type_expense']}\n'
              f'Цена: {res['price']}\n'
              f'Дата: {res['date']}\n',
              reply_markup=admin_kb
            )
        await state.clear()


# продажи

@admin_router.message(F.text=='Продажи')
async def prodazhi(message: types.Message):
    await message.answer('Что хотите сделать?', reply_markup=prodazhi_kb)


# добавить товар

class Add_product(StatesGroup):
    name = State()
    vyplata = State()
    check = State()


@admin_router.message(F.text=='Добавить товар')
async def add_product(message: types.Message, state: FSMContext):
    await message.answer('Введите название товара')
    await state.set_state(Add_product.name)

@admin_router.message(Add_product.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Отлично, а теперь выплату')
    await state.set_state(Add_product.vyplata)


@admin_router.message(Add_product.vyplata, F.text)
async def add_vyplata(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(vyplata=int(message.text))
        res = await state.get_data()
        await message.answer(f'Отлично, все ли верно?\n'
                             f'Название: {res['name']}\n'
                             f'Выплата: {res['vyplata']}\n',
                             reply_markup=yes_no())
        await state.set_state(Add_product.check)
    else:
        await message.answer('Выплата-это число, введи заново')
        await state.set_state(Add_product.vyplata)


@admin_router.callback_query(Add_product.check, F.data)
async def agree(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.delete()
    res = await state.get_data()
    if callback.data == 'yes':
        await orm_add_product(session, res)
        await callback.message.answer(f'Отлично, записал.\n'
            f'Название: {res['name']}\n'
            f'Выплата: {res['vyplata']}\n',
            reply_markup=admin_kb
        )
        await state.clear()
    else:
        await callback.message.answer(f'Отлично, отменил.\n'
              f'Название: {res['name']}\n'
              f'Выплата: {res['vyplata']}\n',
              reply_markup=admin_kb
            )
        await state.clear()


# добавить продажу

class Add_sale(StatesGroup):
    name = State()
    price = State()
    day = State()
    month = State()
    date = State()
    check = State()

@admin_router.message(F.text=='Добавить продажу')
async def add_sell(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer('Что продали?', reply_markup=await products_kbds(session))
    await state.set_state(Add_sale.name)

@admin_router.callback_query(Add_sale.name, F.data)
async def add_name_sell(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.update_data(name=callback.data)
    await callback.message.answer('Отлично, а теперь сумму продажи!', reply_markup=ReplyKeyboardRemove())
    await state.set_state(Add_sale.price)


@admin_router.message(Add_sale.price, F.text)
async def add_droduct_price(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(price=int(message.text))
        await message.answer('Отлично, а теперь дату продажи', reply_markup=await calendar_month())
        await state.set_state(Add_sale.date)
    else:
        await message.answer('Цена-это число, введи заново')
        await state.set_state(Add_sale.price)

# calendar

@admin_router.callback_query(Add_sale.date, F.data)
async def calendaric_month(callback: CallbackQuery, state: FSMContext):
    month=callback.data
    await state.update_data(month=month)
    await callback.message.edit_text('Выберите дату', reply_markup=await calendar_day(month))
    await state.set_state(Add_sale.day)


@admin_router.callback_query(Add_sale.day)
async def calendaric_day(callback: CallbackQuery, state: FSMContext):
    day=callback.data
    if day=='назад':
        await callback.message.edit_text('Выберите месяц', reply_markup=await calendar_month())
        await state.set_state(Add_sale.month)
    else:
        await state.update_data(day=day)
        meet = await state.get_data()
        month = meet['month']
        day = meet['day']
        if int(day) < 10:
            day = '0' + day
        months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
                  'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
        month = str(months.index(month) + 1)
        if int(month) < 10:
            month = '0' + month
        date = str(datetime.now().year) + '-' + month + '-' + day
        await state.update_data(date=date)
        await callback.message.delete()
        res = await state.get_data()
        await callback.message.answer(
            f'Товар: {res['name']}\n'
            f'Цена: {res['price']}\n'
            f'Дата: {res['date']}\n',
            reply_markup=yes_no()
        )
        await state.set_state(Add_sale.check)

@admin_router.callback_query(Add_sale.check, F.data)
async def check_sell(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.delete()
    res = await state.get_data()
    if callback.data == 'yes':
        await orm_add_sell(session, res)
        await callback.message.answer(f'Отлично, записал.\n'
              f'Название: {res['name']}\n'
              f'Цена: {res['price']}\n'
              f'Дата: {res['date']}\n',
              reply_markup=admin_kb
              )
        await state.clear()
    else:
        await callback.message.answer(f'Отлично, отменил.\n'
              f'Название: {res['name']}\n'
              f'Цена: {res['price']}\n'
              f'Дата: {res['date']}\n',
              reply_markup=admin_kb
              )
        await state.clear()


# продажи за месяц
@admin_router.message(F.text=='Продажи за месяц')
async def sell_month(message: types.Message, session: AsyncSession):
    summa=0
    msg=f'Продажи за текущий месяц:\n'
    count=1
    for i in await orm_get_sell_by_month(session, datetime.now().year, datetime.now().month):
        msg+=f'{count}. {i.date} была продана {i.name} за {i.price} рублей\n'
        summa+=i.price
        count+=1
    msg+=f'Суммарные продажи в этом месяце состивили {summa} рублей'
    await message.answer(msg, reply_markup=admin_kb)


# прибль

@admin_router.message(F.text=='Прибыль')
async def income(message: types.Message):
    await message.answer('Какую прибль хотите узнать?', reply_markup=income_kb)


@admin_router.message(F.text=='Прибыль за месяц')
async def income_month(message: types.Message, session: AsyncSession):
    await message.answer(f'{await month_income(session)}', reply_markup=admin_kb)


@admin_router.message(F.text=='Суммарная прибль')
async def income_month(message: types.Message, session: AsyncSession):
    await message.answer(f'{await all_income(session)}', reply_markup=admin_kb)


@admin_router.message(F.text=='Выплаты')
async def vyplaty(message: types.Message, session: AsyncSession):
    await message.answer('Что хотите узнать?', reply_markup=vyplaty_kb)





