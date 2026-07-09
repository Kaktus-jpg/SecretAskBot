from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.database.requests import get_user
from bot.keyboards import main_menu
from bot.misc import get_sub, already_sub

sub = Router()


@sub.callback_query(F.data == "sub")
@sub.message(Command("sub"))
async def subscription(event: Message | CallbackQuery):
    user_id = event.from_user.id
    user = await get_user(user_id=user_id)
    if isinstance(event, Message):
        if not user.is_sub:
            await event.answer(get_sub, reply_markup=await main_menu())
        else:
            await event.answer(already_sub, reply_markup=await main_menu())
    elif isinstance(event, CallbackQuery):
        if not user.is_sub:
            await event.message.edit_text(text=get_sub, reply_markup=await main_menu())
        else:
            await event.message.edit_text(
                text=already_sub, reply_markup=await main_menu()
            )
