import asyncio
import logging

# import redis.asyncio as aioredis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage

# from aiogram.fsm.storage.redis import RedisStorage

from bot import BOT_TOKEN, admin, anons, commands, create_tables, sub, user

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.disabled = True
logging.getLogger("aiogram.event").setLevel(logging.CRITICAL)
logging.getLogger("aiogram.dispatcher").setLevel(logging.CRITICAL)


async def main() -> None:
    # redis = aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
    # storage = RedisStorage(
    #     redis=redis,
    #     key_builder=DefaultKeyBuilder(with_destiny=True),
    # )
    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)
    dp.include_routers(anons, user, sub, admin)
    await bot.set_my_commands(commands=commands)
    await create_tables()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


async def on_startup(dispatcher: Dispatcher):
    logger.info("Bot starting up...")


async def on_shutdown(dispatcher: Dispatcher):
    logger.info("Bot shutting down...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt, SystemExit:
        logger.info("Bot stopped")
