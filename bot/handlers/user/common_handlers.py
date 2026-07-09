from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
)
from aiogram.utils.deep_linking import create_start_link

from bot.database.requests import set_user
from bot.keyboards import share_link
from bot.misc import start_text


user = Router()


@user.callback_query(F.data.in_(("start", "restart")))
@user.message(CommandStart())
async def simple_start(
    event: Message | CallbackQuery, bot: Bot, state: FSMContext
) -> None:
    user_id = event.from_user.id
    first_name = event.from_user.first_name
    second_name = event.from_user.last_name
    username = event.from_user.username
    await set_user(
        user_id=user_id,
        first_name=first_name,
        second_name=second_name,
        username=username,
    )
    await state.clear()

    owner_code = f"user_{user_id}"
    personal_link = await create_start_link(
        bot=bot,
        payload=owner_code,
        encode=True,
    )
    clear_link = personal_link.removeprefix("https://")

    if isinstance(event, Message):
        await bot.delete_message(message_id=event.message_id - 1, chat_id=event.chat.id)

        await event.answer(
            start_text.format(personal_link=clear_link),
            reply_markup=await share_link(personal_link=clear_link),
        )

    elif isinstance(event, CallbackQuery):
        await event.answer()

        if event.data == "restart":
            await event.message.answer(
                start_text.format(personal_link=clear_link),
                reply_markup=await share_link(personal_link=clear_link),
            )

        elif event.data == "start":
            await event.message.edit_text(
                text=start_text.format(personal_link=clear_link),
                reply_markup=await share_link(personal_link=clear_link),
            )
