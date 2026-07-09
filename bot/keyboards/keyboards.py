from urllib.parse import quote

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.database.requests import get_user
from bot.misc.settings import ADMIN_IDS


async def main_button(
    text: str = "В главное меню 🏠", callback: str = "start"
) -> InlineKeyboardButton:
    start_button = InlineKeyboardButton(text=text, callback_data=callback)
    return start_button


async def main_menu() -> InlineKeyboardMarkup:
    start_button = await main_button()
    return InlineKeyboardMarkup(inline_keyboard=[[start_button]])


async def share_link(personal_link: str) -> InlineKeyboardMarkup:
    full_text = (
        f"По этой ссылке можно прислать мне анонимное сообщение:\n👉 {personal_link}"
    )

    share_url = f"t.me/share/url?url={quote(full_text)}"

    share_button = InlineKeyboardButton(
        text="Поделиться ссылкой",
        icon_custom_emoji_id="5361600266225326825",
        url=share_url,
        style=ButtonStyle.PRIMARY,
    )

    return InlineKeyboardMarkup(inline_keyboard=[[share_button]])


async def cancel() -> InlineKeyboardMarkup:
    cancel_button = InlineKeyboardButton(text="❌ Отмена", callback_data="start")
    return InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])


async def another_mes(receiver_id: int) -> InlineKeyboardMarkup:
    another_button = InlineKeyboardButton(
        text="Написать ещё одно ✍️", callback_data=f"user_{receiver_id}"
    )
    main_menu = await main_button()
    return InlineKeyboardMarkup(inline_keyboard=[[another_button], [main_menu]])


async def anons_markup(receiver_id):
    user = await get_user(user_id=receiver_id)

    if not user.is_sub:
        who_is_button = InlineKeyboardButton(text="Кто это? 👀", callback_data="sub")
    answer = InlineKeyboardButton(text="Ответить 📩", callback_data="answer")
    if receiver_id in ADMIN_IDS:
        add_admin = InlineKeyboardButton(
            text="Снять / поднять до админа", callback_data="admin"
        )
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[who_is_button], [answer], [add_admin]]
    )
    return markup
