# Chinaki Bot

Telegram бот для управления каналом и реферальной системой.

## Функциональность

- Управление постами в канале
- Реферальная система
- Система жалоб
- Административная панель
- Управление расходами и доходами

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Milashka2007/chinaki_bot.git
cd chinaki_bot
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv .venv
source .venv/bin/activate  # для Linux/Mac
# или
.venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r req.txt
```

4. Создайте файл `.env` и добавьте необходимые переменные окружения:
```
TOKEN=your_bot_token
```

5. Создайте файл `config.py` и добавьте необходимые ID:
```python
# Admin IDs
ADMIN_IDS = {
    "MAIN_ADMIN": your_main_admin_id,
    "SECOND_ADMIN": your_second_admin_id
}

# Channel IDs
CHANNEL_IDS = {
    "MAIN": your_main_channel_id,
    "POSTS": your_posts_channel_id
}

# Bot Username
BOT_USERNAME = "your_bot_username"
```

6. Инициализируйте базу данных:
```bash
python database/init_db.py
```

## Запуск

```bash
python main.py
```

## Структура проекта

- `handlers/` - обработчики команд и сообщений
- `buttons/` - клавиатуры и кнопки
- `database/` - модели и ORM
  - `init_db.py` - скрипт инициализации базы данных
- `work_chinaki/` - дополнительная функциональность
- `middlewares/` - промежуточные обработчики

## База данных

Проект использует SQLite базу данных. При первом запуске база данных будет создана автоматически. Если вам нужно пересоздать базу данных, просто удалите файл `my_base.db` (если он существует) и запустите `python database/init_db.py`.

## Лицензия

MIT 
