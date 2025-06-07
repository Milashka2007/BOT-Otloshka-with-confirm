import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TOKEN = os.getenv('TOKEN')

# Channel IDs
CHANNEL_IDS = {
    "MAIN": "-1002365174263",
    "POSTS": "-1002282392522"
}

# Bot Username
BOT_USERNAME = "test_kanal_chinaki"

# Admin IDs
ADMIN_IDS = {
    "MAIN_ADMIN": 916539100,  # Главный администратор
    "SECOND_ADMIN": 5208369611  # Второй администратор
}