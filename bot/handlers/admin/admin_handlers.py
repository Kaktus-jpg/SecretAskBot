import asyncio

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

from bot.database import get_user
from bot.misc import increase_to_sub_text

admin = Router()


@admin.callback_query(F.data.startswith("subscriber_"))
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
