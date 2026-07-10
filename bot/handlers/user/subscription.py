import asyncio
from datetime import timedelta

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery

from bot.database import Payment, User, get_last_paid_payment, get_user, set_payment
from bot.keyboards import (
    get_sub,
    get_sub_choose,
    main_menu,
    main_with_clear,
    payment_keyboard,
)
from bot.misc import (
    get_subscription_text,
    success_payment_text,
    successful_refund_text,
    unsupported_refund_text,
)
from bot.utils.utils import get_subscription_status_text, utcnow

sub = Router()
REFUND_WINDOW = timedelta(days=7)


def mark_payment_refunded(payment: Payment, user: User) -> None:
    now = utcnow()

    payment.status = "refunded"
    payment.refunded_at = now
    payment.save()

    user.is_sub = False
    user.save()


@sub.callback_query(F.data.in_(("sub", "re_sub")))
@sub.message(Command("sub"))
async def subscription(event: Message | CallbackQuery):
    user_id = event.from_user.id
    user = await asyncio.to_thread(get_user, user_id)

    if not user.is_sub:
        if isinstance(event, Message):
            await event.answer(
                get_subscription_text, reply_markup=await get_sub_choose()
            )
        elif isinstance(event, CallbackQuery):
            await event.answer()

            if event.data == "sub":
                await event.message.edit_text(
                    text=get_subscription_text, reply_markup=await get_sub_choose()
                )

            elif event.data == "re_sub":
                await event.message.answer(
                    text=get_subscription_text, reply_markup=await get_sub_choose()
                )
    else:
        text = await asyncio.to_thread(get_subscription_status_text, user)

        if isinstance(event, Message):
            await event.answer(
                text,
                reply_markup=await main_menu(),
            )

        elif isinstance(event, CallbackQuery):
            await event.answer()

            if event.data == "sub":
                await event.message.edit_text(
                    text,
                    reply_markup=await main_menu(),
                )
            else:
                await event.message.answer(
                    text,
                    reply_markup=await main_menu(),
                )


@sub.callback_query(F.data == "buy_with_xtr")
async def buy_with_xtr(callback: CallbackQuery, state: FSMContext):
    currency = "XTR"
    prices = [LabeledPrice(label=currency, amount=50)]

    await callback.message.delete()
    mes = await callback.message.answer_invoice(
        title="Покупка подписки",
        description="Покупка подписки за 50 звёзд навсегда",
        prices=prices,
        provider_token="",
        payload="subscription",
        currency=currency,
        reply_markup=await payment_keyboard(),
    )
    await state.update_data(purchase_message_id=mes.message_id)


@sub.message(Command("refund"))
async def refund_cmd(message: Message, bot: Bot):
    user = await asyncio.to_thread(get_user, message.from_user.id)

    if not user.is_sub:
        await message.answer(
            unsupported_refund_text,
            reply_markup=await get_sub(),
        )
        return

    payment = await asyncio.to_thread(get_last_paid_payment, user)

    if payment is None:
        await message.answer(
            "Не удалось найти платёж для возврата. "
            "Если ты оплатил подписку недавно — обратись в поддержку.",
            reply_markup=await main_menu(),
        )
        return

    now = utcnow()

    if now > payment.refund_until:
        await message.answer(
            "Срок возврата истёк.\n\n"
            "Подписка остаётся активной навсегда, "
            "повторных списаний не будет.",
            reply_markup=await main_menu(),
        )
        return

    # Помечаем запрос как обрабатываемый до обращения к Telegram.
    payment.status = "refunding"
    await asyncio.to_thread(payment.save)

    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=payment.telegram_payment_charge_id,
        )

    except TelegramBadRequest:
        # Telegram не принял возврат — возвращаем платёж в доступное состояние.
        payment.status = "paid"
        await asyncio.to_thread(payment.save)

        await message.answer(
            "Не удалось выполнить возврат. " "Возможно, платёж уже был возвращён.",
            reply_markup=await main_menu(),
        )
        return

    except Exception as exc:
        payment.status = "paid"
        await asyncio.to_thread(payment.save)

        await message.answer(
            "Не удалось выполнить возврат. Попробуй позже.\n\n"
            f"Техническая информация: {type(exc).__name__}",
            reply_markup=await main_menu(),
        )
        return

    await asyncio.to_thread(mark_payment_refunded, payment, user)

    await message.answer(
        successful_refund_text,
        reply_markup=await get_sub(),
    )


@sub.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@sub.message(F.successful_payment)
async def process_successful_payment(message: Message, state: FSMContext):
    data = await state.get_data()
    purchase_message_id = data.get("purchase_message_id")
    transaction_id = message.successful_payment.telegram_payment_charge_id
    invoice_payload = message.successful_payment.invoice_payload
    amount_xtr = message.successful_payment.total_amount
    status = "paid"

    # Выдать подписку, записать платёж и т. д.

    text = success_payment_text.format(transaction_id=transaction_id)

    sub_user = await asyncio.to_thread(get_user, message.from_user.id)

    now = utcnow()

    sub_user.is_sub = True
    sub_user.save()

    await asyncio.to_thread(
        set_payment,
        sub_user,
        transaction_id,
        invoice_payload,
        amount_xtr,
        now,
        now + REFUND_WINDOW,
        None,
        status,
    )

    if purchase_message_id:
        await message.bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=purchase_message_id,
            reply_markup=None,
        )

    await message.answer(
        text,
        message_effect_id="5104841245755180586",
        reply_markup=await main_with_clear(),
    )
