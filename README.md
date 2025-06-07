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
git clone https://github.com/your-username/chinaki_bot.git
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

## Запуск

```bash
python main.py
```

## Структура проекта

- `handlers/` - обработчики команд и сообщений
- `buttons/` - клавиатуры и кнопки
- `database/` - модели и ORM
- `work_chinaki/` - дополнительная функциональность
- `middlewares/` - промежуточные обработчики

## Лицензия

MIT 