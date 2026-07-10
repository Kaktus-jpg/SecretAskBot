import asyncio

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.requests import (
    get_anonymous_message,
    get_user,
    close_anonymous_message,
    set_anonymous_message,
)
from bot.keyboards import anons_markup, another_mes, cancel
from bot.misc import answer_text
from bot.misc.texts import (
    message_sent_text,
    receive_message_text,
    receive_sub_message_text,
)
from bot.states import ReceiverStates
from bot.utils import AnonymousReplyCallback, send_anonymous_message

receiver = Router()


@receiver.callback_query(AnonymousReplyCallback.filter())
async def answer_sender_callback(
    callback: CallbackQuery,
    callback_data: AnonymousReplyCallback,
    state: FSMContext,
) -> None:
    anonymous_message = await asyncio.to_thread(
        get_anonymous_message,
        callback_data.anonymous_message_id,
    )

    if anonymous_message is None or not anonymous_message.is_active:
        await callback.answer(
            "На это сообщение уже нельзя ответить.",
            show_alert=True,
        )
        return

    if anonymous_message.receiver_id != callback.from_user.id:
        await callback.answer(
            "Эта кнопка не для вас.",
            show_alert=True,
        )
        return

    await callback.answer()

    prompt = await callback.message.answer(
        answer_text,
        reply_markup=await cancel(),
    )

    await state.set_state(ReceiverStates.wait_for_answer_message)
    await state.update_data(
        anonymous_message_id=anonymous_message.id,
        data_id=prompt.message_id,
    )


@receiver.message(ReceiverStates.wait_for_answer_message)
async def get_answer(
    message: Message,
    state: FSMContext,
    bot: Bot,
) -> None:
    data = await state.get_data()

    anonymous_message_id = data.get("anonymous_message_id")
    prompt_message_id = data.get("data_id")

    if anonymous_message_id is None:
        await state.clear()
        await message.answer(
            "Не удалось определить сообщение для ответа. Попробуй ещё раз."
        )
        return

    # Получаем постоянную связь из SQLite:
    # sender_id — автор исходного сообщения,
    # receiver_id — текущий получатель, который отвечает.
    anonymous_message = await asyncio.to_thread(
        get_anonymous_message,
        anonymous_message_id,
    )

    # Запись удалили / кнопка больше недействительна / ответ уже был отправлен.
    if anonymous_message is None or not anonymous_message.is_active:
        await state.clear()
        await message.answer("На это сообщение больше нельзя ответить.")
        return

    sender_id = anonymous_message.sender_id
    receiver_id = anonymous_message.receiver_id

    # Вторая проверка: нельзя отправить ответ от лица другого пользователя,
    # даже если у него почему-либо осталось чужое FSM-состояние.
    if receiver_id != message.from_user.id:
        await state.clear()
        await message.answer("Нельзя отправить ответ на это сообщение.")
        return

    # Убираем клавиатуру «Отмена» под текстом-инструкцией.
    if prompt_message_id:
        try:
            await bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=prompt_message_id,
                reply_markup=None,
            )
        except Exception:
            pass

    # Пользователь, которому уходит ответ — исходный sender.
    sender_user = await asyncio.to_thread(
        get_user,
        sender_id,
    )

    if sender_user.is_sub:
        text = receive_sub_message_text.format(
            user_id=message.from_user.id,
            name=message.from_user.first_name,
        )
    else:
        text = receive_message_text

    # Отправляем ответ исходному автору.
    # ВАЖНО: здесь пока можно сохранить существующую логику,
    # но дальше лучше и ответ тоже записывать в AnonymousMessage,
    # чтобы создавать полноценную цепочку диалога.
    delivered_message = await send_anonymous_message(
        bot=bot,
        target_chat_id=sender_id,
        source_message=message,
        reply_markup=None,
        header_text=text,
    )

    if delivered_message is None:
        await state.clear()
        await message.answer("Не удалось отправить ответ. Попробуй ещё раз позже.")
        return

    # Создаём НОВУЮ запись для ответного анонимного сообщения.
    # Текущий receiver написал ответ -> он становится sender.
    # Исходный sender получает ответ -> он становится receiver.
    reply_anonymous_message = await asyncio.to_thread(
        set_anonymous_message,
        receiver_id,  # Автор анонимного ответа
        sender_id,  # Получатель анонимного ответа
        delivered_message.message_id,
    )

    # Теперь исходный отправитель тоже может нажать «Ответить 📩».
    await bot.edit_message_reply_markup(
        chat_id=sender_id,
        message_id=delivered_message.message_id,
        reply_markup=await anons_markup(
            receiver_id=sender_id,
            sender_id=receiver_id,
            anonymous_message_id=reply_anonymous_message.id,
        ),
    )

    # Пока разрешаем один ответ на исходное сообщение.
    # Удали этот вызов, если получатель может отвечать много раз.
    await asyncio.to_thread(
        close_anonymous_message,
        anonymous_message.id,
    )

    await state.clear()

    mes = await message.answer(
        message_sent_text,
        reply_markup=await another_mes(receiver_id=sender_id),
    )

    # Эти значения нужны твоему существующему обработчику
    # «отправить ещё одно сообщение».
    await state.update_data(
        sender_id=receiver_id,
        continue_id=mes.message_id,
    )
