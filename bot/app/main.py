import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from . import config, lead, menu, portfolio


async def run() -> None:
    logging.basicConfig(level=logging.INFO)
    session = AiohttpSession(proxy=config.TG_PROXY) if config.TG_PROXY else None
    bot = Bot(
        config.BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(lead.router)
    dp.include_router(portfolio.router)
    dp.include_router(menu.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
