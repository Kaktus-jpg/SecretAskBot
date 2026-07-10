import asyncio
import logging

from bot.database.requests import (
    delete_old_anonymous_messages,
    delete_closed_anonymous_messages,
)


async def cleanup_anonymous_messages_task() -> None:
    while True:
        try:
            active_deleted_count = await asyncio.to_thread(
                delete_old_anonymous_messages,
                30,
            )

            closed_deleted_count = await asyncio.to_thread(
                delete_closed_anonymous_messages,
                3,
            )

            logging.info(
                "Удалено старых активных анонимных сообщений: %s",
                active_deleted_count,
            )
            logging.info(
                "Удалено старых закрытых анонимных сообщений: %s",
                closed_deleted_count,
            )

        except Exception:
            logging.exception("Ошибка при очистке старых анонимных сообщений")

        # Повторить очистку через 24 часа.
        await asyncio.sleep(24 * 60 * 60)
