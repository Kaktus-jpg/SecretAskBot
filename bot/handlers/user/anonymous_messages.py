import asyncio

from aiogram import Bot, F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.payload import decode_payload

from bot.database import (
    get_user,
    set_anonymous_message,
    set_user,
)
from bot.keyboards import anons_markup, another_mes, cancel, main_menu
from bot.misc import (
    admin_texts,
    anonym_send_text,
    message_sent_text,
    receive_message_text,
    receive_sub_message_text,
    your_link_text,
)
from bot.states import SenderStates
from bot.utils import send_anonymous_message

anons = Router()


@anons.message(CommandStart(deep_link=True))
async def deep_start(
    message: Message, command: CommandObject, state: FSMContext, bot: Bot
):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    second_name = message.from_user.last_name

    await asyncio.to_thread(set_user, user_id, username, first_name, second_name)

    payload = decode_payload(command.args)

    receiver_id = int(payload.removeprefix("user_"))
    sender_id = user_id

    # await state.set_state(SenderStates.wait_for_send_message)
    # await state.update_data(receiver_id=receiver_id)
    #
    # mes = await message.answer(anonym_send_text, reply_markup=await cancel())
    #
    # await state.update_data(data_id=mes.message_id)

    if receiver_id != sender_id:
        await state.set_state(SenderStates.wait_for_send_message)
        await state.update_data(receiver_id=receiver_id)
        mes = await message.answer(anonym_send_text, reply_markup=await cancel())
        await state.update_data(data_id=mes.message_id)
    else:
        await message.answer(your_link_text, reply_markup=await main_menu())
        await state.clear()


@anons.message(SenderStates.wait_for_send_message)
async def get_anon_mes(message: Message, state: FSMContext, bot: Bot):
    receiver_id = await state.get_value("receiver_id")
    sender_id = message.from_user.id

    get_data_mes_id = await state.get_value("data_id")

    receiver = await asyncio.to_thread(get_user, receiver_id)
    if get_data_mes_id:
        try:
            await bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=get_data_mes_id,
                reply_markup=None,
            )
        except Exception:
            pass

    if receiver.is_sub:
        text = receive_sub_message_text.format(
            user_id=message.from_user.id, name=message.from_user.first_name
        )
    else:
        text = receive_message_text
    delivered_message = await send_anonymous_message(
        bot=bot,
        target_chat_id=receiver_id,
        source_message=message,
        reply_markup=None,
        header_text=text,
    )
    if delivered_message is None:
        return

    anonymous_message = await asyncio.to_thread(
        set_anonymous_message,
        sender_id,
        receiver_id,
        delivered_message.message_id,
    )

    await bot.edit_message_reply_markup(
        chat_id=receiver_id,
        message_id=delivered_message.message_id,
        reply_markup=await anons_markup(
            receiver_id=receiver_id,
            sender_id=sender_id,
            anonymous_message_id=anonymous_message.id,
        ),
    )

    await state.clear()
    mes = await message.answer(
        message_sent_text,
        reply_markup=await another_mes(receiver_id=receiver_id),
    )
    await state.update_data(sender_id=sender_id)
    await state.update_data(continue_id=mes.message_id)


@anons.callback_query(F.data.startswith("user_"))
async def deep_call(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
) -> None:
    await callback.answer()

    # Сначала читаем временный ID сообщения «Сообщение отправлено».
    continue_message_id = await state.get_value("continue_id")

    # Затем убираем у него клавиатуру.
    if continue_message_id:
        try:
            await bot.edit_message_reply_markup(
                chat_id=callback.message.chat.id,
                message_id=continue_message_id,
                reply_markup=None,
            )
        except Exception:
            pass

    receiver_id = int(callback.data.removeprefix("user_"))

    # Теперь можно очистить данные предыдущего сценария.
    await state.clear()

    # Запускаем новый сценарий отправки.
    await state.set_state(SenderStates.wait_for_send_message)
    await state.update_data(receiver_id=receiver_id)

    prompt = await callback.message.answer(
        anonym_send_text,
        reply_markup=await cancel(),
    )

    await state.update_data(data_id=prompt.message_id)


@anons.callback_query(F.data.startswith("admin_"))
async def deep_call_from_btn(callback: CallbackQuery, state: FSMContext):
    mod, receiver_id = callback.data.split("_", maxsplit=2)[1:3]

    # Теперь можно очистить данные предыдущего сценария.
    await state.clear()

    # Запускаем новый сценарий отправки.
    await state.set_state(SenderStates.wait_for_send_message)
    await state.update_data(receiver_id=int(receiver_id))

    text = admin_texts[mod]

    prompt = await callback.message.edit_text(
        text,
        reply_markup=await cancel(),
    )

    await state.update_data(data_id=prompt.message_id)
