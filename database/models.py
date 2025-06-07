
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.testing.schema import mapped_column
from sqlalchemy import String, DateTime, func, Date, Integer, Text, ForeignKey, event, BigInteger
from datetime import date, datetime
import importlib
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
def get_bot():
    return bot


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Sale(Base):
    __tablename__ = "sale"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[DateTime] = mapped_column(String(100), nullable=False)


class Buy(Base):
    __tablename__ = "buy"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)


class Product(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    vyplata: Mapped[str] = mapped_column(String(100), nullable=False)


class Investor(Base):
    __tablename__ = "investor"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    procent_doxod: Mapped[int] = mapped_column(Integer, nullable=False)
    vklad: Mapped[int] = mapped_column(Integer, nullable=False)
    ostalos_plat: Mapped[int] = mapped_column(Integer, nullable=False)
    procent_ot_dohoda: Mapped[int] = mapped_column(Integer, nullable=False)


class Post(Base):
    __tablename__ = "post"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    publish_date: Mapped[date] = mapped_column(Date, default=False)
    publish_time: Mapped[str] = mapped_column(String(150), nullable=True)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    # Связь с медиафайлами
    media: Mapped[list["Media"]] = relationship("Media", back_populates="post", cascade="all, delete-orphan")



@event.listens_for(Post, "after_update", propagate=True)
def track_status_change(mapper, connection, target):
    if "status" in target.__dict__:
        new_status = target.status
        if new_status == 'На проверке':
            asyncio.create_task(handle_post_check())

async def handle_post_check():
    post_module = importlib.import_module('handlers.post')  # импортируйте модуль handlers.post динамически
    check_post = getattr(post_module, 'yvedomlenie')  # получите функцию check_post
    await check_post(get_bot())



class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Например, "photo" или "video"
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id", ondelete="CASCADE"), nullable=False)

    # Связь с постом
    post: Mapped["Post"] = relationship("Post", back_populates="media")


class UserStatistics(Base):
    __tablename__ = "user_statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Уникальный идентификатор записи
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)  # Telegram ID пользователя
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)  # Полное имя пользователя
    join_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)   # Время присоединения к каналу
    messages_in_comments_count: Mapped[int] = mapped_column(Integer, default=0)  # Кол-во сообщений в комментариях
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    time_mute: Mapped[int] = mapped_column(Integer, default=0)


class FormerUsers(Base):
    __tablename__ = "FormerUsers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Уникальный идентификатор записи
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)  # Telegram ID пользователя
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)  # Полное имя пользователя
    left_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)


#все роли
# ref - обычный реф, admin - обычный админ, main_admin - главный админ(только 1), boss - владелец(только 1)

class Admins(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    privedeno_today: Mapped[int] = mapped_column(Integer, nullable=False)
    privedeno_vsego: Mapped[int] = mapped_column(Integer, nullable=False)
    vyplata: Mapped[int] = mapped_column(Integer, nullable=False)


class Zhaloba(Base):
    __tablename__ = "zhaloba"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    kto_otpravil: Mapped[str] = mapped_column(String(255), nullable=False)
    na_kogo_otpravili: Mapped[str] = mapped_column(String(255), nullable=False)
