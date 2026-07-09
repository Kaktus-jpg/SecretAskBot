import os

from dotenv import load_dotenv

if not load_dotenv():
    exit("Файл .env не найден или не был создан!")


# переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = {int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()}
