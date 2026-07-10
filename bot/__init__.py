from bot.database import create_tables
from bot.handlers import admin, anons, receiver, sub, user
from bot.misc import BOT_TOKEN, commands
from bot.utils import cleanup_anonymous_messages_task
