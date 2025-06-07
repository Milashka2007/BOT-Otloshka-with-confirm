from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import CallbackQuery

from buttons.buttons_admin import yes_no, admin_kb, investor_kbds
from database.orm import orm_add_investor, orm_sellect_investors, orm_update_ostalos_plat, orm_delete_investor
from handlers.proc import vyplaty

investor_router = Router()

class Investor(StatesGroup):
    name = State()
    procent_dohod = State()
    vklad = State()
    ostalos_plat = State()
    check = State()
    procent_ot_dohoda= State()

@investor_router.message(F.text=='Добавить инвестора')
async def investor(message: types.Message, state: FSMContext):
    await message.answer('Введите имя инвестора', reply_markup=ReplyKeyboardRemove())
    await state.set_state(Investor.name)


@investor_router.message(Investor.name, F.text)
async def investor_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Отлично, теперь введи проценты инвестора')
    await state.set_state(Investor.procent_dohod)


@investor_router.message(Investor.procent_dohod, F.text)
async def investor_dohod(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await message.answer('Отлично, а теперь скажи мне сумму вклада')
        await state.update_data(procent_dohod=message.text)
        await state.set_state(Investor.vklad)
    else:
        await message.answer('Проценты-это число, введи заново')
        await state.set_state(Investor.procent_dohod)


@investor_router.message(Investor.vklad, F.text)
async def investor_vklad(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(vklad=message.text)
        res= await state.get_data()
        ost=int(res['vklad'])+int(res['vklad'])*int(res['procent_dohod'])//100
        await state.update_data(ostalos_plat=ost)
        await message.answer('А сколько инвестор будет получать процентов от дохода?')
        await state.set_state(Investor.procent_ot_dohoda)
    else:
        await message.answer('Вклад-это число, введи заново')
        await state.set_state(Investor.vklad)

@investor_router.message(Investor.procent_ot_dohoda, F.text)
async def investor_vyplata_ot_dohoda(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(procent_ot_dohoda=message.text)
        res = await state.get_data()
        await message.answer(f'Отлично! Добавляем инвестора?\n'
                 f'Имя инвестора - {res['name']}\n'
                 f'Процент инвестора - {res["procent_dohod"]}\n'
                 f'Вклад инвестора - {res["vklad"]}\n'
                 f'Суммарная выручка инвестора - {res["ostalos_plat"]}\n'
                 f'Процент от дохода - {res['procent_ot_dohoda']}\n',
                 reply_markup=yes_no()
            )
        await state.set_state(Investor.check)
    else:
        await message.answer('Процент от дохода - это число, введи заново')
        await state.set_state(Investor.procent_ot_dohoda)


@investor_router.callback_query(Investor.check, F.data)
async def investor_check(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.delete()
    res = await state.get_data()
    if callback.data == 'yes':
        await orm_add_investor(session, res)
        await callback.message.answer(f'Отлично! Добавил инвестора!\n'
                 f'Имя инвестора - {res["name"]}\n'
                 f'Процент инвестора - {res["procent_dohod"]}\n'
                 f'Вклад инвестора - {res["vklad"]}\n'
                 f'Суммарная выручка инвестора - {res["ostalos_plat"]}\n'
                 f'Процент от дохода - {res["procent_ot_dohoda"]}\n',
            reply_markup=admin_kb)
        await state.clear()
    else:
        await callback.message.answer(f'Отлично! Не добавил инвестора!\n'
                 f'Имя инвестора - {res['name']}\n'
                 f'Процент инвестора - {res["procent_dohod"]}\n'
                 f'Вклад инвестора - {res["vklad"]}\n'
                 f'Суммарная выручка инвестора - {res["ostalos_plat"]}\n'
                 f'Процент от дохода - {res['procent_ot_dohoda']}\n',
            reply_markup=admin_kb)
        await state.clear()


@investor_router.message(F.text=='Узнать выплаты')
async def sdelati_vyplaty(message: types.Message, session: AsyncSession):
    await message.answer(await vyplaty(session))


class Pay(StatesGroup):
    name = State()
    much = State()
    check = State()


@investor_router.message(F.text=='Cделать выплату')
async def make_vyplata(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer(f'Вот все текущие инвесторы, выберите того, кому хотите выплатить.\n{await vyplaty(session)}', reply_markup=await investor_kbds(session))
    await state.set_state(Pay.name)


@investor_router.callback_query(Pay.name, F.data)
async def name_investor_pat(callback: CallbackQuery, state: FSMContext):
    name=callback.data
    await callback.message.delete()
    await state.update_data(name=name)
    await callback.message.answer(f'Отлично! Какую выплату сделаем инвестору {name}?', reply_markup=ReplyKeyboardRemove())
    await state.set_state(Pay.much)


@investor_router.message(F.text, Pay.much)
async def much_investor_name(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text.isdigit():
        await state.update_data(much=message.text)
        res=await state.get_data()
        name=res["name"]
        investor=await orm_sellect_investors(session, name)
        vyplata_text = "\n".join([
            f"Выплата {i.name} составила {res['much']}\n"
            f"Долг до выплаты - {i.ostalos_plat}\n"
            f"Долг после выплаты - {i.ostalos_plat-int(res['much'])}\n"
            for i in investor])

        await message.answer(f'Отлично, подтверждаю выплату?\n{vyplata_text}', reply_markup=yes_no())
        await state.set_state(Pay.check)
    else:
        await message.answer('Выплата-это число, введи заново')
        await state.set_state(Pay.much)


@investor_router.callback_query(Pay.check, F.data)
async def check_vyplata(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if callback.data == 'yes':
        await callback.message.delete()
        res = await state.get_data()
        name = res["name"]
        investor = await orm_sellect_investors(session, name)
        new_ost=0
        for i in investor:
            new_ost=i.ostalos_plat - int(res['much'])
        vyplata_text = "\n".join([
            f"Выплата {i.name} составила {res['much']}\n"
            f"Долг до выплаты - {i.ostalos_plat}\n"
            f"Долг после выплаты - {new_ost}\n"
            for i in investor])
        await orm_update_ostalos_plat(session, name, new_ost)
        await callback.message.answer(f'Отлично, выплата сделана!\n{vyplata_text}', reply_markup=admin_kb)
        await state.clear()
    else:
        await callback.message.delete()
        await callback.message.answer('Выплата отменена!', reply_markup=admin_kb)
        await state.clear()

class Del(StatesGroup):
    investor = State()

@investor_router.message(F.text=='Удалить инвестора')
async def ydalit_investora(message: types.Message, session: AsyncSession, state: FSMContext):
    await message.answer('Какого инвестора вы хотите удалить?', reply_markup = await investor_kbds(session))
    await state.set_state(Del.investor)

@investor_router.callback_query(Del.investor, F.data)
async def del_investor(callback: CallbackQuery, session: AsyncSession):
    investor=callback.data
    await callback.message.delete()
    await orm_delete_investor(session, investor)
    await callback.message.answer('Инвестор удален', reply_markup=admin_kb)

