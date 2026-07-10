import asyncio

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandObject, Command, Filter
from aiogram.types import CallbackQuery, Message
from pydantic import ValidationError

from bot.database import get_user, get_payment, Payment
from bot.keyboards import main_menu, get_sub
from bot.misc import (
    increase_to_sub_text,
    no_args_refund_text,
    already_refunded_text,
    successful_refund_text,
    unsupported_refund_text,
)
from bot.misc import ADMIN_IDS
from bot.utils import utcnow

admin = Router()


class AdminFilter(Filter):
    async def __call__(
        self,
        event: Message | CallbackQuery,
    ) -> bool:
        return event.from_user is not None and event.from_user.id in ADMIN_IDS


@admin.callback_query(AdminFilter(), F.data.startswith("subscriber_"))
async def increase(callback: CallbackQuery, bot: Bot):
    sub_id = int(callback.data.removeprefix("subscriber_"))
    sub = await asyncio.to_thread(get_user, sub_id)
    if sub.is_sub:
        await callback.answer(f"{sub.first_name} уже подписчик!")
    else:
        sub.is_sub = True
        sub.save()
        await callback.answer(
            f"{sub.first_name} теперь подписчик!\nСообщение ему отправлено"
        )
        await bot.send_message(sub_id, increase_to_sub_text)


@admin.message(AdminFilter(), Command("admin_refund"))
async def admin_refund(
    message: Message,
    bot: Bot,
    command: CommandObject,
):
    charge_id = (command.args or "").strip()

    if not charge_id:
        await message.answer(
            "Использование:\n" "<code>/admin_refund ID_ОПЕРАЦИИ</code>"
        )
        return

    payment = await asyncio.to_thread(
        get_payment,
        charge_id,
    )

    if payment is None:
        await message.answer("Платёж с таким ID не найден в базе.")
        return

    if payment.status == "refunded" or payment.refunded_at is not None:
        await message.answer("Этот платёж уже был возвращён.")
        return

    if payment.status == "refunding":
        await message.answer(
            "Этот возврат уже обрабатывается. Попробуй проверить позже."
        )
        return

    # Блокирует повторный /admin_refund, пока Telegram отвечает.
    payment.status = "refunding"
    await asyncio.to_thread(
        payment.save,
        only=[Payment.status],
    )

    try:
        await bot.refund_star_payment(
            user_id=payment.user.user_id,
            telegram_payment_charge_id=(payment.telegram_payment_charge_id),
        )

    except TelegramBadRequest as exc:
        # Возврат не прошёл: позволяем повторить попытку.
        payment.status = "paid"
        await asyncio.to_thread(
            payment.save,
            only=[Payment.status],
        )

        await message.answer(
            "Telegram не выполнил возврат.\n\n" f"<code>{exc.message}</code>"
        )
        return

    except Exception as exc:
        payment.status = "paid"
        await asyncio.to_thread(
            payment.save,
            only=[Payment.status],
        )

        await message.answer(
            "Не удалось выполнить возврат из-за технической ошибки.\n\n"
            f"<code>{type(exc).__name__}: {exc}</code>"
        )
        return

    now = utcnow()

    payment.status = "refunded"
    payment.refunded_at = now
    await asyncio.to_thread(
        payment.save,
        only=[Payment.status, Payment.refunded_at],
    )

    # Для lifetime-подписки отключаем доступ после возврата.
    payment.user.is_sub = False
    await asyncio.to_thread(
        payment.user.save,
        only=[payment.user.__class__.is_sub],
    )

    await message.answer(
        "Возврат выполнен.\n\n"
        f"Пользователь: <code>{payment.user.user_id}</code>\n"
        f"Сумма: <b>{payment.amount_xtr} Stars</b>\n"
        f"Операция: <code>{payment.telegram_payment_charge_id}</code>"
    )
