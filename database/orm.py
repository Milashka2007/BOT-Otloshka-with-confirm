from datetime import datetime, date
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sympy.physics.units import nanometer

from database.models import Sale, Buy, Product, Investor, Post, Media, UserStatistics, Admins, FormerUsers, Zhaloba


async def orm_add_buy(session: AsyncSession, data: dict):
    obj = Buy(
        type=data["type_expense"],
        price=data["price"],
        date=datetime.strptime(data["date"], '%Y.%m.%d').date()
    )
    session.add(obj)
    await session.commit()


async def orm_get_expenses_by_month(session: AsyncSession, year: int | str, month: int | str):
    year = str(year)
    month = f"{int(month):02}"
    year_month = f"{year}-{month}%"
    query = select(Buy).where(Buy.date.like(year_month))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_product(session: AsyncSession, data: dict):
    obj = Product(
        name=data["name"],
        vyplata=data["vyplata"]
    )
    session.add(obj)
    await session.commit()


async def orm_get_all_products_kbds(session: AsyncSession):
    query=select(Product)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_sell(session: AsyncSession, data: dict):
    obj = Sale(
        name=data["name"],
        price=data["price"],
        date=data["date"]
    )
    session.add(obj)
    await session.commit()


async def orm_get_sell_by_month(session: AsyncSession, year: int | str, month: int | str):
    year = str(year)
    month = f"{int(month):02}"
    year_month = f"{year}-{month}%"
    query = select(Sale).where(Sale.date.like(year_month))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_all_sale(session: AsyncSession):
    query=select(Sale)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_all_expenses(session: AsyncSession):
    query=select(Buy)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_investor(session: AsyncSession, data: dict):
    obj = Investor(
        name=data["name"],
        procent_doxod=data["procent_dohod"],
        vklad=data["vklad"],
        ostalos_plat=data["ostalos_plat"],
        procent_ot_dohoda=data["procent_ot_dohoda"]
    )
    session.add(obj)
    await session.commit()

async def orm_get_investors(session: AsyncSession):
    query = select(Investor)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_sellect_investors(session: AsyncSession, names: str):
    query = select(Investor).where(Investor.name == names)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_update_ostalos_plat(session: AsyncSession, name: str, new_value: int):
    query = update(Investor).where(Investor.name == name).values(ostalos_plat=new_value)
    await session.execute(query)
    await session.commit()


async def orm_delete_investor(session: AsyncSession, name: str):
    query = delete(Investor).where(Investor.name == name)
    await session.execute(query)
    await session.commit()


async def orm_add_post_with_media(session: AsyncSession, text: str, media_files: list[dict], publish_time: str, publish_date: date, status: str):
    new_post = Post(
        text=text,
        publish_date=publish_date,
        publish_time = publish_time,
        status = status,
        media=[
            Media(file_id=file["file_id"], media_type=file["type"]) for file in media_files
        ]
    )
    session.add(new_post)
    await session.commit()


async def orm_get_posts_with_media_details_by_status(session, status: str):
    # Создаем ORM-запрос
    query = (
        select(Post)
        .options(selectinload(Post.media))  # Загружаем связанные медиа
        .where(Post.status == status)       # Фильтруем посты по статусу
    )
    result = await session.execute(query)
    posts = result.scalars().all()

    # Возвращаем посты с ограниченным набором данных из медиа
    return [
        {
            "post": post,
            "media_details": [
                {"file_id": media.file_id, "media_type": media.media_type}
                for media in post.media
            ],
        }
        for post in posts
    ]


async def orm_get_post_with_media_details_by_id(session, post_id: int):
    # Создаем ORM-запрос
    query = (
        select(Post)
        .options(selectinload(Post.media))  # Загружаем связанные медиа
        .where(Post.id == post_id)  # Фильтруем посты по ID
    )

    result = await session.execute(query)
    post = result.scalar_one_or_none()  # Получаем один пост (или None, если не найдено)

    if post:
        # Возвращаем пост и медиа-данные
        return {
            "post": post,
            "media_details": [
                {"file_id": media.file_id, "media_type": media.media_type}
                for media in post.media
            ],
        }
    return None  # Если пост не найден, возвращаем None


async def orm_update_status(session: AsyncSession, old_status: str, new_status: str):
    posts = await session.execute(
        select(Post).where(Post.status == old_status)
    )
    posts_to_update = posts.scalars().all()

    for post in posts_to_update:
        post.status = new_status

    await session.commit()
    return posts_to_update


async def orm_update_status_by_id(session: AsyncSession, id: int, new_status: str):
    posts = await session.execute(
        select(Post).where(Post.id == id)
    )
    posts_to_update = posts.scalars().all()

    for post in posts_to_update:
        post.status = new_status

    await session.commit()
    return posts_to_update

async def orm_delete_post(session: AsyncSession, post_id: int):
    # Удаляем строки из таблицы Media, где post_id совпадает
    delete_media_query = delete(Media).where(Media.post_id == post_id)
    await session.execute(delete_media_query)

    # Удаляем пост из таблицы Post
    delete_post_query = delete(Post).where(Post.id == post_id)
    await session.execute(delete_post_query)

    # Применяем изменения
    await session.commit()

async def orm_update_text_post_by_id(session: AsyncSession, post_id: int, text: str):
    query = update(Post).where(Post.id == post_id).values(text=text)
    await session.execute(query)
    await session.commit()


async def orm_add_user(session, user_id: int, full_name: str, ref='None'):
    # Проверка существующего пользователя
    query = select(UserStatistics).where(UserStatistics.user_id == user_id)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return None
    # Получаем текущую дату и время
    current_datetime = datetime.utcnow()  # Время в формате DateTime (включая дату и время)

    # Создаем нового пользователя с текущим временем
    new_user = UserStatistics(
        user_id=user_id,
        full_name=full_name,
        join_date=current_datetime,  # Подставляем текущую дату и время
        messages_in_comments_count=0,
        warning_count=0,
        time_mute=0,
    )
    # Добавление нового пользователя в сессию
    session.add(new_user)
    await session.commit()  # Коммитим изменения

async def orm_add_left_user(session, user_id: int, full_name: str, reason: str):
    query = select(FormerUsers).where(FormerUsers.user_id == user_id)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return None
    current_datetime = datetime.utcnow()  # Время в формате DateTime (включая дату и время)

    # Создаем нового пользователя с текущим временем
    new_user = FormerUsers(
        user_id=user_id,
        full_name=full_name,
        left_date=current_datetime,  # Подставляем текущую дату и время
        reason=reason,
    )
    # Добавление нового пользователя в сессию
    session.add(new_user)
    await session.commit()  # Коммитим изменения



async def increment_comment_count(session: AsyncSession, user_id: int):
    # Создаем запрос для получения пользователя по user_id
    query = select(UserStatistics).where(UserStatistics.user_id == user_id)

    # Выполняем запрос
    result = await session.execute(query)
    user = result.scalars().first()  # Получаем первого пользователя (или None, если не найдено)

    if user:
        # Если пользователь найден, увеличиваем счетчик сообщений в комментариях
        update_query = update(UserStatistics).where(UserStatistics.user_id == user_id).values(
            messages_in_comments_count=UserStatistics.messages_in_comments_count + 1
        )
        await session.execute(update_query)  # Выполняем обновление
        await session.commit()  # Подтверждаем изменения


async def is_user_in_db(session: AsyncSession, user_id: int) -> bool:
    query = select(UserStatistics).where(UserStatistics.user_id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()  # Получаем первого пользователя или None

    return user is not None

async def is_user_in_kicked_db(session: AsyncSession, user_id: int) -> bool:
    query = select(FormerUsers).where(FormerUsers.user_id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()  # Получаем первого пользователя или None

    return user is not None


async def delete_user_from_db(session: AsyncSession, user_id: int) -> bool:

    query = delete(UserStatistics).where(UserStatistics.user_id == user_id)
    result = await session.execute(query)  # Выполняем запрос
    await session.commit()  # Подтверждаем изменения


async def delete_user_from_kicked_db(session: AsyncSession, user_id: int) -> bool:

    query = delete(FormerUsers).where(FormerUsers.user_id == user_id)
    result = await session.execute(query)  # Выполняем запрос
    await session.commit()  # Подтверждаем изменения

#ref

async def orm_ref_exists(session: AsyncSession, ref_id: int):
    query = select(1).where(Admins.user_id == ref_id)  # Запрашиваем только наличие записи
    result = await session.execute(query)
    return result.scalar() is not None

async def orm_add_ref(session: AsyncSession, user_id: int, full_name: str, role: str):
    new_admin = Admins(
        user_id=user_id,
        full_name=full_name,
        role=role,
        privedeno_today=0,
        privedeno_vsego=0,
        vyplata=0
    )

    session.add(new_admin)
    await session.commit()


async def orm_get_referrer_by_user_id(session, user_id):
    query = select(Admins.user_id).where(Admins.user_id == user_id)
    result = await session.execute(query)
    referrer = result.scalar_one_or_none()
    return referrer


async def orm_increment_referral_count(session, referrer_id):
    query = (
        update(Admins)
        .where(Admins.user_id == referrer_id)
        .values(privedeno_vsego=Admins.privedeno_vsego + 1)
    )
    await session.execute(query)
    await session.commit()

async def orm_get_admins(session: AsyncSession):
    query = select(Admins).where(Admins.role == 'admin', Admins.role == 'main_admin', Admins.role == 'boss')
    result = await session.execute(query)
    return result.scalars().all()

async def orm_add_zhaloba(session: AsyncSession, link, kto, na_kogo, id):
    new_zhaloba = Zhaloba(
        text=link,
        kto_otpravil=kto,
        na_kogo_otpravili=na_kogo,
    )
    session.add(new_zhaloba)
    await session.commit()


async def orm_get_zhaloba(session: AsyncSession):
    query = select(Zhaloba)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_zhaloba_by_id(session, zhaloba_id):
    query = select(Zhaloba).where(Zhaloba.id == zhaloba_id)
    result = await session.execute(query)
    return result.scalars().all()