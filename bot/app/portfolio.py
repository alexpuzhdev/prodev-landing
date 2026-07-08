import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from . import keyboards, screen
from .backend import backend
from .menu import FALLBACK_ERROR, texts

router = Router()
log = logging.getLogger(__name__)


async def show_item(callback: CallbackQuery, state: FSMContext, idx: int) -> None:
    bot = callback.bot
    chat_id = callback.message.chat.id
    try:
        t = await texts()
        items = await backend.portfolio()
    except Exception:
        log.exception("backend unavailable on portfolio")
        await callback.answer(FALLBACK_ERROR, show_alert=True)
        return
    if not items:
        await screen.show_text(bot, chat_id, state, t["botPortfolioEmpty"], keyboards.back_menu(t))
        await callback.answer()
        return
    idx = max(0, min(idx, len(items) - 1))
    item = items[idx]
    caption = f"<b>{item['title']}</b>\n\n{item['text']}"
    markup = keyboards.portfolio_nav(t, idx, len(items))
    try:
        data = await backend.image(item["image_path"])
        await screen.show_bytes(bot, chat_id, state, item["image_path"], data, caption, markup)
    except Exception:
        log.exception("portfolio image failed")
        await screen.show_text(bot, chat_id, state, caption, markup)
    await callback.answer()


@router.callback_query(F.data == "menu:portfolio")
async def open_portfolio(callback: CallbackQuery, state: FSMContext) -> None:
    await show_item(callback, state, 0)


@router.callback_query(F.data.startswith("portfolio:"))
async def navigate(callback: CallbackQuery, state: FSMContext) -> None:
    idx = int(callback.data.split(":", 1)[1])
    await show_item(callback, state, idx)
