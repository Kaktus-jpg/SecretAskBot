import math
from datetime import timezone

from zoneinfo import ZoneInfo
from bot.database import get_last_paid_payment
from bot.misc import already_subscription_text
from bot.utils import utcnow


def get_subscription_status_text(user) -> str:
    payment = get_last_paid_payment(user)

    if payment is None:
        return (
            "<b>У тебя уже есть подписка ✨</b>\n\n"
            "Статус: <i>Premium навсегда</i>\n"
            "Срок возврата истёк или информация о платеже отсутствует."
        )

    now = utcnow()

    if now > payment.refund_until:
        return (
            "<b>У тебя уже есть подписка ✨</b>\n\n"
            "С ней ты можешь узнавать, <b>кто отправил тебе анонимное сообщение</b>.\n\n"
            "• Статус: <i>Premium навсегда</i>\n"
            "• Срок возврата истёк\n"
            "• Автопродления нет"
        )

    seconds_left = (payment.refund_until - now).total_seconds()
    days_left = max(1, math.ceil(seconds_left / 86400))

    msk = ZoneInfo("Europe/Moscow")

    refund_until = payment.refund_until

    if refund_until.tzinfo is None:
        refund_until = refund_until.replace(tzinfo=timezone.utc)

    return already_subscription_text.format(
        remaining_at=refund_until.astimezone(msk).strftime("%d.%m.%Y %H:%M МСК"),
        remaining_days=days_left,
    )
