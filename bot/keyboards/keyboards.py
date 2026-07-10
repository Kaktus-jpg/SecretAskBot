import asyncio
from urllib.parse import quote

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.requests import get_user
from bot.misc.settings import ADMIN_IDS
from bot.utils import AnonymousReplyCallback


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

    sub = InlineKeyboardButton(
        text="Подписка",
        callback_data="sub",
        icon_custom_emoji_id="5897658922600240288",
        style=ButtonStyle.SUCCESS,
    )

    return InlineKeyboardMarkup(inline_keyboard=[[share_button], [sub]])


async def cancel() -> InlineKeyboardMarkup:
    cancel_button = InlineKeyboardButton(
        text="Отмена ❌", callback_data="start", style=ButtonStyle.DANGER
    )
    return InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])


async def another_mes(receiver_id: int) -> InlineKeyboardMarkup:
    another_button = InlineKeyboardButton(
        text="Написать ещё одно ✍️", callback_data=f"user_{receiver_id}"
    )
    start_manu = await main_button(callback="restart_clear_markup")
    return InlineKeyboardMarkup(inline_keyboard=[[another_button], [start_manu]])


async def anons_markup(
    receiver_id: int,
    sender_id: int,
    anonymous_message_id: int,
) -> InlineKeyboardMarkup:
    receiver = await asyncio.to_thread(get_user, receiver_id)
    sender = await asyncio.to_thread(get_user, sender_id)

    builder = InlineKeyboardBuilder()

    if not receiver.is_sub:
        builder.row(
            InlineKeyboardButton(
                text="Кто это? 👀",
                callback_data="re_sub",
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="Ответить 📩",
            callback_data=AnonymousReplyCallback(
                anonymous_message_id=anonymous_message_id,
            ).pack(),
        )
    )

    if receiver_id in ADMIN_IDS:
        if not sender.is_sub:
            to_subscriber = InlineKeyboardButton(
                text="Выдать подписку 💸", callback_data=f"subscriber_{sender_id}"
            )
            builder.row(to_subscriber)

    return builder.as_markup()


async def get_sub_choose() -> InlineKeyboardMarkup:
    write = InlineKeyboardButton(
        text="Написать 5 предложений ✍️", callback_data="admin_sub_7902315226"
    )
    buy_with_xtr = InlineKeyboardButton(
        text="Купить за 50 звёзд ⭐", callback_data="buy_with_xtr"
    )
    start_menu = await main_button()
    return InlineKeyboardMarkup(inline_keyboard=[[write], [buy_with_xtr], [start_menu]])


async def payment_keyboard() -> InlineKeyboardMarkup:
    pay_button = InlineKeyboardButton(text="Оплатить 50 ⭐", pay=True)
    cancel_button = InlineKeyboardButton(
        text="Отмена ❌", callback_data="restart_delete"
    )

    return InlineKeyboardMarkup(inline_keyboard=[[pay_button], [cancel_button]])


async def get_sub() -> InlineKeyboardMarkup:
    buy_sub_button = InlineKeyboardButton(
        text="Приобрести подписку 🌠", callback_data="sub"
    )
    start_menu = await main_button()
    return InlineKeyboardMarkup(inline_keyboard=[[buy_sub_button], [start_menu]])


async def help_menu() -> InlineKeyboardMarkup:
    write_help = InlineKeyboardButton(
        text="Написать в поддержку ✏️", callback_data="admin_help_7902315226"
    )
    start_menu = await main_button()
    return InlineKeyboardMarkup(inline_keyboard=[[write_help], [start_menu]])


async def main_with_clear() -> InlineKeyboardMarkup:
    start_button = await main_button(callback="restart_clear_markup")
    return InlineKeyboardMarkup(inline_keyboard=[[start_button]])
