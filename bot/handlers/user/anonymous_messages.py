from aiogram import Bot, Router, F
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.payload import decode_payload

from bot.database.requests import get_user
from bot.keyboards import cancel, another_mes
from bot.misc import (
    anonym_send_text,
    message_sent_text,
    receive_message_text,
)
from bot.misc.texts import receive_sub_message_text
from bot.states import SenderStates
from bot.utils import send_anonymous_message


anons = Router()


@anons.message(CommandStart(deep_link=True))
async def deep_start(
    message: Message, command: CommandObject, state: FSMContext, bot: Bot
):
    payload = decode_payload(command.args)

    recipient_id = int(payload.removeprefix("user_"))
    user_id = int(message.from_user.id)

    await state.set_state(SenderStates.wait_for_send_message)
    await state.update_data(recipient_id=recipient_id)

    mes = await message.answer(anonym_send_text, reply_markup=await cancel())

    await state.update_data(data_id=mes.message_id)

    # if recipient_id != user_id:
    #     await state.set_state(SenderStates.wait_for_send_message)
    #     await state.update_data(recipient_id=recipient_id)
    #     mes = await message.answer(anonym_send_text, reply_markup=await cancel())
    #     await state.update_data(data_id=mes.message_id)
    # else:
    #     await message.answer(your_link_text)
    #     await state.clear()


@anons.message(SenderStates.wait_for_send_message)
async def get_anon_mes(message: Message, state: FSMContext, bot: Bot):
    recipient_id = await state.get_value("recipient_id")
    get_data_mes_id = await state.get_value("data_id")

    user = await get_user(user_id=recipient_id)

    if get_data_mes_id:
        try:
            await bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=get_data_mes_id,
                reply_markup=None,
            )
        except Exception:
            pass

    if user.is_sub:
        text = receive_sub_message_text.format(
            user_id=message.from_user.id, name=message.from_user.first_name
        )
    else:
        text = receive_message_text
    await send_anonymous_message(
        bot=bot,
        target_chat_id=recipient_id,
        source_message=message,
        header_text=text,
    )
    await state.clear()
    mes = await message.answer(
        message_sent_text, reply_markup=await another_mes(receiver_id=recipient_id)
    )
    await state.update_data(continue_id=mes.message_id)


@anons.callback_query(F.data.startswith("user_"))
async def deep_call(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    get_continue_mes_id = await state.get_value("continue_id")

    if get_continue_mes_id:
        try:
            await bot.edit_message_reply_markup(
                chat_id=callback.message.chat.id,
                message_id=get_continue_mes_id,
                reply_markup=None,
            )
        except Exception:
            pass

    recipient_id = int(callback.data.removeprefix("user_"))
    user_id = int(callback.from_user.id)

    await state.set_state(SenderStates.wait_for_send_message)
    await state.update_data(recipient_id=recipient_id)

    mes = await callback.message.answer(anonym_send_text, reply_markup=await cancel())

    await state.update_data(data_id=mes.message_id)

    # if recipient_id != user_id:
    #     await state.set_state(SenderStates.wait_for_send_message)
    #     await state.update_data(recipient_id=recipient_id)
    #     await message.answer(anonym_send_text, reply_markup=await cancel())
    # else:
    #     await message.answer(your_link_text)
    #     await state.clear()
