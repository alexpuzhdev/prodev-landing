import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from . import config, lead, menu, portfolio


async def run() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(lead.router)
    dp.include_router(portfolio.router)
    dp.include_router(menu.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
