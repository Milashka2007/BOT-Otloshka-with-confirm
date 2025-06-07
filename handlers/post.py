from curses.ascii import isdigit

from aiogram import Router, types, F
from aiogram.filters import Command, or_f
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.media_group import MediaGroupBuilder
from datetime import datetime, date
from buttons.buttons_user import confirm_kb, start_post, post_kb, otpravit_post, da_net_kb, referalka, work_chanel, zhaloba_kbds
from sqlalchemy.ext.asyncio import AsyncSession
from buttons.html import convert_to_html
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os
from buttons.calendar import calendar_month, calendar_day, calendar_time
from database.orm import orm_add_post_with_media, orm_update_status, orm_get_posts_with_media_details_by_status, \
    orm_get_post_with_media_details_by_id, orm_delete_post, orm_update_status_by_id, orm_update_text_post_by_id, orm_get_zhaloba
from database.engine import session_maker
from config import ADMIN_IDS, CHANNEL_IDS

post_router = Router()

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


class PostStates(StatesGroup):
    text = State()
    media = State()
    month = State()
    day = State()
    time = State()
    date = State()
    check_post = State()
    status = State()
    confirm = State()


@post_router.message(Command('start'))
async def start(message: types.Message):
    if message.from_user.id in [ADMIN_IDS["MAIN_ADMIN"], ADMIN_IDS["SECOND_ADMIN"]]:
        await message.answer('Дарова, ты в меню админа', reply_markup=await start_post(message))

@post_router.message(F.text=='Работа с каналом')
async def ref_admin(message: types.Message):
    await message.answer('Что делаем?', reply_markup= work_chanel)


@post_router.message(F.text=='Посмотреть жалобы')
async def ref_admin(message: types.Message, session: AsyncSession):
    zhaloby = await orm_get_zhaloba(session)
    await message.answer('Вот все новые жалобы:', reply_markup= work_chanel)
    for i in zhaloby:
        await message.answer(f'Пользователь {i.kto_otpravil} отправил жалобу на {i.na_kogo_otpravili}\n\nСсылка на жалобу - {i.text}', parse_mode=ParseMode.HTML, reply_markup = await zhaloba_kbds(session, i.id))



@post_router.message(F.text == 'Сделать пост')
async def start_add_post(message: types.Message, state: FSMContext):
    msg = (f'Форматы текста:\n'
           f'%%ЖИРНЫЙ%%\n'
           f'^^КУРСИВ^^\n'
           f';;ЗАЧЕРКНУТЫЙ;;\n'
           f'!!МОНОШИРИННЫЙ!!\n'
           f'&&ЦИТАТА&&\n'
           f'№№ССЫЛКА№ ТЕКСТ №№\n'
           f'Введите текст поста:')
    await message.answer(msg, reply_markup=ReplyKeyboardRemove())
    await state.set_state(PostStates.text)


@post_router.message(PostStates.text, F.text)
async def get_post_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Отправьте медиафайлы (фото или видео). Завершите отправку командой /done.")
    await state.set_state(PostStates.media)


count = 0


@post_router.message(PostStates.media, or_f(F.photo, F.video))
async def get_post_media(message: types.Message, state: FSMContext):
    media_type = "photo" if message.photo else "video"
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id

    data = await state.get_data()
    media_files = data.get("media", [])
    global count
    if count < 10:
        media_files.append({"file_id": file_id, "type": media_type})
        count += 1
        await state.update_data(media=media_files)
        await message.answer(
            f"Медиафайл добавлен.\nМаксимум медиафайлов - 10.\nЗагружено - {count}\nОтправьте следующий файл или завершите командой /done.")
    else:
        await message.answer(
            'Загружено максимально количество файлов, дальнейшая загрузка невозможна!\nНажмите /done для завершения')


# calendar
@post_router.callback_query(F.data == 'year')
async def calendaric_year(callback: CallbackQuery):
    current_year = str(datetime.now().year)
    await callback.answer(f'Текущий год-{current_year}')


@post_router.callback_query(F.data == 'weekday')
@post_router.callback_query(F.data == 'month')
async def calendaric_month(callback: CallbackQuery, state: FSMContext):
    meet = await state.get_data()
    month = meet['month']
    await callback.answer(f'Текущий месяц-{month}')


@post_router.message(Command("done"))
async def make_meet(message: types.Message, state: FSMContext):
    res = await state.get_data()
    if len(res) == 1:
        await message.answer('Вы не добавили фото! Пришлите их заново')
        await state.set_state(PostStates.media)
    else:
        global count
        count = 0
        await message.answer('Выберите месяц', reply_markup=await calendar_month())
        await state.set_state(PostStates.month)


@post_router.callback_query(PostStates.month)
async def calendaric_month(callback: CallbackQuery, state: FSMContext):
    month = callback.data
    await state.update_data(month=month)
    await callback.message.edit_text('Выберите дату', reply_markup=await calendar_day(month))
    await state.set_state(PostStates.day)


@post_router.callback_query(PostStates.day)
async def calendaric_day(callback: CallbackQuery, state: FSMContext):
    day = callback.data
    if day == 'назад':
        await callback.message.edit_text('Выберите месяц', reply_markup=await calendar_month())
        await state.set_state(PostStates.month)
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
        date = day + '.' + month
        await callback.message.edit_text('Выберите время', reply_markup=await calendar_time(date))
        await state.set_state(PostStates.time)


@post_router.callback_query(PostStates.time)
async def select_name(callback: CallbackQuery, state: FSMContext):
    time = callback.data
    await state.update_data(time=time)
    meet = await state.get_data()
    month = meet['month']
    day = meet['day']
    time = meet['time']
    if time == 'назад':
        await callback.message.edit_text('Выберите дату', reply_markup=await calendar_day(month))
        await state.set_state(PostStates.day)
    else:
        await callback.message.delete()
        if int(day) < 10:
            day = '0' + day
        months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
                  'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
        month = str(months.index(month) + 1)
        if int(month) < 10:
            month = '0' + month
        date = str(datetime.now().year) + '-' + month + '-' + day
        await state.update_data(date=date)
        await callback.message.answer(f'Отлично, вот пост!')
        # post
        data = await state.get_data()
        text = data["text"]
        media_files = data.get("media", [])

        text = convert_to_html(text)
        text += '\n' + '\n💻' + '<a href="https://t.me/chinaki_news">CHINAKI</a>'
        await state.update_data(text=text)
        # Создаем список объектов InputMedia для отправки медиафайлов
        photos = MediaGroupBuilder(
            caption=text
        )
        for file in media_files:
            if file['type'] == 'photo':
                photos.add_photo(file['file_id'])  # Передаем file_id через именованный аргумент
            elif file['type'] == 'video':
                photos.add_video(file['file_id'])  # Передаем file_id через именованный аргумент

        # Если есть медиафайлы, отправляем их как медиа-группу
        await callback.message.answer_media_group(media=photos.build())  # Все медиа отправляются в одном сообщении
        await callback.message.answer(f"Пост будет выложен в {data['time']} {data['date']} числа, все ли верно?",
                                      reply_markup=confirm_kb)
        await state.set_state(PostStates.confirm)


@post_router.message(PostStates.confirm, F.text == "Отменить ❌")
async def cancel_post(message: types.Message, state: FSMContext):
    await message.answer("Добавление поста отменено.", reply_markup=await start_post(message))
    await state.clear()


@post_router.message(PostStates.confirm, F.text == "Подтвердить ✅")
async def send_post(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(status='Ждет обновления')
    res = await state.get_data()
    res['date'] = datetime.strptime(res['date'], "%Y-%m-%d").date()
    await orm_add_post_with_media(
        session=session,
        text=res['text'],  # Текст поста
        media_files=res['media'],  # Список медиафайлов
        publish_time=res['time'],  # Время публикации
        publish_date=res['date'],  # Дата публикации
        status=res['status']  # Статус поста
    )
    await orm_update_status(session, 'Ждет обновления', 'На проверке')
    await message.answer('Отлично, отправил пост на проверку!', reply_markup=await start_post(message))
    await state.clear()


async def yvedomlenie(bot: Bot):
    await bot.send_message(ADMIN_IDS["MAIN_ADMIN"], 'Новый пост ждет проверки!')


@post_router.message(F.text == 'Новые посты')
async def see_posts(message: types.Message, session: AsyncSession):
    posts = await orm_get_posts_with_media_details_by_status(session, 'На проверке')
    x = 0
    for i in posts:
        post = i["post"]
        post_id = post.id
        post_text = f'ID поста - {post_id}\n' + f'Время выгрузки: {post.publish_date} в {post.publish_time}⬇️\n\n' + post.text

        photos = MediaGroupBuilder(
            caption=post_text
        )

        media_details = i["media_details"]
        for media in media_details:
            file_id = media["file_id"]
            media_type = media["media_type"]

            if media_type == 'photo':
                photos.add_photo(file_id)
            if media_type == 'video':
                photos.add_video(file_id)

        await message.answer_media_group(media=photos.build())
        x += 1
    if x == 0:
        await message.answer('Новых постов нет(')


class AgreePost(StatesGroup):
    check = State()
    confirm = State()
    id = State()
    text = State()
    check2 = State()
    confirm2 = State()


async def get_post_with_media_details_by_id(session: AsyncSession, id: int, post_text=''):
    posts = await orm_get_post_with_media_details_by_id(session, id)
    post = posts['post']
    media_details = posts['media_details']
    if post_text == '':
        photos = MediaGroupBuilder(
            caption=post.text
        )
    else:
        photos = MediaGroupBuilder(
            caption=post_text
        )

    for media in media_details:
        file_id = media["file_id"]
        media_type = media["media_type"]

        if media_type == 'photo':
            photos.add_photo(file_id)
        if media_type == 'video':
            photos.add_video(file_id)

    return photos


@post_router.message(F.text == 'Изменить/Подтвердить пост')
async def agree_posts(message: types.Message, state: FSMContext):
    await message.answer('Напиши ID поста который хочешь изменить', reply_markup=ReplyKeyboardRemove())
    await state.set_state(AgreePost.id)


@post_router.message(F.text, AgreePost.id)
async def text_post(message: types.Message, state: FSMContext, session: AsyncSession):
    posts = await orm_get_post_with_media_details_by_id(session, int(message.text))
    if posts:
        post = posts['post']
    if posts == None:
        await message.answer('Поста с таким id нет(', reply_markup=await start_post(message))
    if post.status != 'На проверке':
        await message.answer('Этот пост не находится на проверке', reply_markup=await start_post(message))
    else:
        if message.text.isdigit():
            await state.update_data(id=int(message.text))
            photos = await get_post_with_media_details_by_id(session, post.id)
            await message.answer_media_group(media=photos.build())
            await message.answer('Что мы с ним делаем?', reply_markup=post_kb)
            await state.set_state(AgreePost.check)
        else:
            await state.clear()


@post_router.message(F.text, AgreePost.check)
async def post_do(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    postik = await state.get_data()

    if message.text == 'Отменить пост❌':
        photos = await get_post_with_media_details_by_id(session, postik['id'])
        await orm_delete_post(session, postik['id'])
        await bot.send_media_group(5208369611, media=photos.build())
        await bot.send_message(5208369611, 'Этот пост был отменен!')

        await message.answer('Пост отменен', reply_markup=await start_post(message))
        await state.clear()

    if message.text == 'Подтвердить пост✅':
        photos = await get_post_with_media_details_by_id(session, postik['id'])
        await orm_update_status_by_id(session, postik['id'], 'Одобрено')
        await bot.send_media_group(5208369611, media=photos.build())
        await bot.send_message(5208369611, 'Этот пост был одобрен!')

        await message.answer('Вы одобрили этот пост', reply_markup=await start_post(message))
        await state.clear()

    if message.text == 'Отправить комментарий⚙️':
        await message.answer('Что вы хотите написать?', reply_markup=ReplyKeyboardRemove())
        await state.set_state(AgreePost.text)

    if message.text == 'Самому изменить пост⚙️':
        await message.answer('Введите полностью новый текст!', reply_markup=ReplyKeyboardRemove())
        await state.set_state(AgreePost.check2)


@post_router.message(F.text, AgreePost.check2)
async def do_myself(message: types.Message, state: FSMContext, session: AsyncSession):
    text = convert_to_html(message.text)
    await state.update_data(text=text)
    res = await state.get_data()
    photos = await get_post_with_media_details_by_id(session, res['id'], text)
    await message.answer_media_group(media=photos.build())
    await message.answer(f'Отправляем?', reply_markup=otpravit_post)
    await state.set_state(AgreePost.confirm2)


@post_router.message(F.text, AgreePost.confirm2)
async def do_myself2(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    if message.text == 'ДА ✅':
        res = await state.get_data()
        photos = await get_post_with_media_details_by_id(session, res['id'])
        await orm_update_text_post_by_id(session, res['id'], res['text'])
        await orm_update_status_by_id(session, res['id'], 'Одобрено')
        await bot.send_media_group(5208369611, media=photos.build())
        await bot.send_message(5208369611,
                               f'Пост одобрен с корректировками!\nКорректировки - {res["text"]}')
        await message.answer('Супер! Пост одобрен!', reply_markup=await start_post(message))
        await state.clear()

    if message.text == 'Нет ❌':
        await message.answer('Подтверждение поста отменено!', reply_markup=await start_post(message))
        await state.clear()

    if message.text == 'Изменить текст⚙️':
        await message.answer('Введите комментарий заново!', reply_markup=ReplyKeyboardRemove())
        await state.set_state(AgreePost.check2)


@post_router.message(F.text, AgreePost.text)
async def final_part_post(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(text=message.text)
    res = await state.get_data()
    photos = await get_post_with_media_details_by_id(session, res['id'])
    await message.answer_media_group(media=photos.build())
    await message.answer(f'Комментарий - {res["text"]}', reply_markup=otpravit_post)
    await state.set_state(AgreePost.confirm)


@post_router.message(F.text, AgreePost.confirm)
async def agree_remake_post(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    if message.text == 'ДА ✅':
        res = await state.get_data()
        photos = await get_post_with_media_details_by_id(session, res['id'])
        await orm_delete_post(session, res['id'])
        await bot.send_media_group(5208369611, media=photos.build())
        await bot.send_message(5208369611,
                               f'Пост удален из базы данных, пересоздай с корректировками!\nКорректировки - {res["text"]}')
        await message.answer('Супер! Ждем отладки!', reply_markup=await start_post(message))
        await state.clear()

    if message.text == 'Нет ❌':
        await message.answer('Подтверждение поста отменено!', reply_markup=await start_post(message))
        await state.clear()

    if message.text == 'Изменить текст⚙️':
        await message.answer('Введите комментарий заново!', reply_markup=ReplyKeyboardRemove())
        await state.set_state(AgreePost.text)


class Otmena(StatesGroup):
    id = State()
    check = State()


@post_router.message(F.text=='Посмотреть посты')
async def otmena_post(message: types.Message, state: FSMContext, session: AsyncSession):
    posts = await orm_get_posts_with_media_details_by_status(session, 'Одобрено')
    if posts:
        for i in posts:
            post = i["post"]
            post_id = post.id
            post_data = post.publish_date
            post_time = post.publish_time
            photos = MediaGroupBuilder(
                caption= f'ID поста - {post_id}\nДата - {post_data}\nВремя - {post_time}\n' + post.text
            )
            media_details = i["media_details"]
            for media in media_details:
                file_id = media["file_id"]
                media_type = media["media_type"]

                if media_type == 'photo':
                    photos.add_photo(file_id)
                if media_type == 'video':
                    photos.add_video(file_id)
            await message.answer_media_group(media=photos.build())
        await message.answer('Хотите удалить пост?', reply_markup=da_net_kb)
        await state.set_state(Otmena.check)
    else:
        await message.answer('Постов в ожидании отправки нет!', reply_markup=await start_post(message))


@post_router.message(F.text, Otmena.check)
async def da_net(message: types.Message, state: FSMContext):
    if message.text == 'ДА ✅':
        await message.answer('Напишите id поста, который хотите удалить!', reply_markup=ReplyKeyboardRemove())
        await state.set_state(Otmena.id)
    if message.text == 'Нет ❌':
        await message.answer('Хорошо, ничего не отменяю!', reply_markup=await start_post(message))


@post_router.message(F.text, Otmena.id)
async def delete_postik(message: types.Message, session: AsyncSession):
    if isdigit(message.text):
        await orm_delete_post(session, int(message.text))
        await message.answer(f'Пост с ID {message.text} успешно удален!', reply_markup=await start_post(message))
    else:
        await message.answer('Вы ввели не число', reply_markup=await start_post(message))


async def load_post(bot: Bot):
    async with session_maker() as session:
        posts = await orm_get_posts_with_media_details_by_status(session, 'Одобрено')
        for i in posts:
            post = i["post"]
            if post.publish_date == date.today():
                if post.publish_time < datetime.now().strftime("%H:%M"):
                    post_id = post.id

                    photos = MediaGroupBuilder(
                        caption=post.text
                    )
                    media_details = i["media_details"]
                    for media in media_details:
                        file_id = media["file_id"]
                        media_type = media["media_type"]

                        if media_type == 'photo':
                            photos.add_photo(file_id)
                        if media_type == 'video':
                            photos.add_video(file_id)
                    await bot.send_media_group(CHANNEL_IDS[0], media=photos.build())
                    await orm_delete_post(session, post_id)



