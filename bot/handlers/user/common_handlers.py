import asyncio

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
)
from aiogram.utils.deep_linking import create_start_link

from bot.database import get_user, set_user
from bot.keyboards import cancel, get_sub, help_menu, main_menu, share_link
from bot.misc import (
    help_cmd_text,
    really_stop_text,
    start_text,
    stop_cmd_text,
    stop_cmd_without_sub_text,
)
from bot.states import StopSub

user = Router()


@user.callback_query(F.data.startswith("restart_"))
@user.callback_query(F.data.in_(("start", "restart")))
@user.message(CommandStart())
async def simple_start(
    event: Message | CallbackQuery, bot: Bot, state: FSMContext
) -> None:
    user_id = event.from_user.id
    username = event.from_user.username
    first_name = event.from_user.first_name
    second_name = event.from_user.last_name
    await asyncio.to_thread(set_user, user_id, username, first_name, second_name)

    await state.clear()

    owner_code = f"user_{user_id}"
    personal_link = await create_start_link(
        bot=bot,
        payload=owner_code,
        encode=True,
    )
    clear_link = personal_link.removeprefix("https://")

    if isinstance(event, Message):
        await event.answer(
            start_text.format(personal_link=clear_link),
            reply_markup=await share_link(personal_link=clear_link),
        )

    elif isinstance(event, CallbackQuery):
        await event.answer()

        if event.data.startswith("restart"):
            if event.data == "restart_clear_markup":
                try:
                    await bot.edit_message_reply_markup(
                        chat_id=event.message.chat.id,
                        message_id=event.message.message_id,
                        reply_markup=None,
                    )
                except Exception:
                    pass

            elif event.data == "restart_delete":
                await event.message.delete()

            await event.message.answer(
                start_text.format(personal_link=clear_link),
                reply_markup=await share_link(personal_link=clear_link),
            )

        elif event.data == "start":
            await event.message.edit_text(
                text=start_text.format(personal_link=clear_link),
                reply_markup=await share_link(personal_link=clear_link),
            )


@user.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(help_cmd_text, reply_markup=await help_menu())


@user.message(Command("stop"))
async def stop_cmd(message: Message, state: FSMContext):
    sub_user = await asyncio.to_thread(get_user, message.from_user.id)
    if not sub_user.is_sub:
        await message.answer(stop_cmd_without_sub_text, reply_markup=await get_sub())
        return
    mes = await message.answer(stop_cmd_text, reply_markup=await cancel())
    await state.set_state(StopSub.get_stop_message)
    await state.update_data(cancel_mes_id=mes.message_id)


@user.message(StopSub.get_stop_message, F.text == "СТОП")
async def totally_sure(message: Message, state: FSMContext, bot: Bot):
    cancel_message_id = await state.get_value("cancel_mes_id")
    unsub_user = await asyncio.to_thread(get_user, message.from_user.id)

    if cancel_message_id:
        try:
            await bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=cancel_message_id,
                reply_markup=None,
            )
        except Exception:
            pass

    await message.answer(really_stop_text, reply_markup=await main_menu())
    unsub_user.is_sub = False
    unsub_user.save()
    await state.clear()
