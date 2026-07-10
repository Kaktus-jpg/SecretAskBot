from aiogram.types import BotCommand

from bot.misc.texts import write_help_text, write_sentences_text

commands = [
    BotCommand(command="start", description="🏠 Главное меню"),
    BotCommand(command="sub", description="⭐ Подписка"),
    BotCommand(command="refund", description="💸 Вернуть деньги"),
    BotCommand(command="stop", description="⛔ Остановить подписку"),
    BotCommand(command="help", description="📲 Помощь"),
]

admin_texts = {"sub": write_sentences_text, "help": write_help_text}
