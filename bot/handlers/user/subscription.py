import asyncio

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from pydantic import ValidationError

from bot.database import User
from bot.database.requests import get_user
from bot.keyboards import (
    main_menu,
    get_sub_choose,
    payment_keyboard,
    get_sub,
    main_with_clear,
)
from bot.misc import (
    get_subscription_text,
    already_subscription_text,
    success_payment_text,
    no_args_refund_text,
    really_stop_text,
    already_refunded_text,
    unsupported_refund_text,
    successful_refund_text,
)

sub = Router()


@sub.callback_query(F.data.in_(("sub", "re_sub")))
@sub.message(Command("sub"))
async def subscription(event: Message | CallbackQuery):
    user_id = event.from_user.id
    user = await asyncio.to_thread(get_user, user_id)

    if isinstance(event, Message):
        if not user.is_sub:
            await event.answer(
                get_subscription_text, reply_markup=await get_sub_choose()
            )
        else:
            await event.answer(
                already_subscription_text, reply_markup=await main_menu()
            )
    elif isinstance(event, CallbackQuery):
        await event.answer()

        if event.data == "sub":
            if not user.is_sub:
                await event.message.edit_text(
                    text=get_subscription_text, reply_markup=await get_sub_choose()
                )
            else:
                await event.message.edit_text(
                    text=already_subscription_text, reply_markup=await main_menu()
                )
        elif event.data == "re_sub":
            if not user.is_sub:
                await event.message.answer(
                    text=get_subscription_text, reply_markup=await get_sub_choose()
                )
            else:
                await event.message.answer(
                    text=already_subscription_text, reply_markup=await main_menu()
                )


@sub.callback_query(F.data == "buy_with_xtr")
async def buy_with_xtr(callback: CallbackQuery, state: FSMContext):
    currency = "XTR"
    prices = [LabeledPrice(label=currency, amount=1)]

    await callback.message.delete()
    mes = await callback.message.answer_invoice(
        title="Покупка подписки",
        description="Покупка подписки за 120 (1) звёзд навсегда",
        prices=prices,
        provider_token="",
        payload="subscription",
        currency=currency,
        reply_markup=await payment_keyboard(),
    )
    await state.update_data(purchase_message_id=mes.message_id)


@sub.message(Command("refund"))
async def refund_cmd(message: Message, bot: Bot, command: CommandObject):
    transaction_id = command.args
    user = await asyncio.to_thread(get_user, message.from_user.id)
    if user.is_sub:

        try:
            await bot.refund_star_payment(
                user_id=message.from_user.id,
                telegram_payment_charge_id=transaction_id,
            )
        except ValidationError:
            await message.answer(no_args_refund_text, reply_markup=await main_menu())
        except TelegramBadRequest:
            await message.answer(already_refunded_text, reply_markup=await get_sub())
        except Exception as exc:
            await message.answer(
                f"‼️ Ошибка: {type(exc).__name__}: {exc}",
                reply_markup=await main_menu(),
            )
        else:
            await message.answer(successful_refund_text, reply_markup=await get_sub())
            user = await asyncio.to_thread(get_user, message.from_user.id)
            user.is_sub = False
            user.save()

    else:
        await message.answer(unsupported_refund_text, reply_markup=await get_sub())


@sub.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@sub.message(F.successful_payment)
async def process_successful_payment(message: Message, state: FSMContext):
    data = await state.get_data()
    purchase_message_id = data.get("purchase_message_id")

    text = success_payment_text.format(
        transaction_id=message.successful_payment.telegram_payment_charge_id
    )

    sub_user = await asyncio.to_thread(get_user, message.from_user.id)
    sub_user.is_sub = True
    sub_user.save()

    # Выдать подписку, записать платёж и т. д.

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
