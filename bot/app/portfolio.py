import logging

from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery

from . import keyboards
from .backend import backend
from .menu import FALLBACK_ERROR, texts

router = Router()
log = logging.getLogger(__name__)


async def show_item(callback: CallbackQuery, idx: int) -> None:
    try:
        t = await texts()
        items = await backend.portfolio()
    except Exception:
        log.exception("backend unavailable on portfolio")
        await callback.answer(FALLBACK_ERROR, show_alert=True)
        return
    if not items:
        await callback.message.answer(t["botPortfolioEmpty"], reply_markup=keyboards.back_menu(t))
        await callback.answer()
        return
    idx = max(0, min(idx, len(items) - 1))
    item = items[idx]
    caption = f"<b>{item['title']}</b>\n\n{item['text']}"
    markup = keyboards.portfolio_nav(t, idx, len(items))
    try:
        data = await backend.image(item["image_path"])
        photo = BufferedInputFile(data, filename="case.png")
        await callback.message.answer_photo(photo, caption=caption, reply_markup=markup)
    except Exception:
        log.exception("portfolio image failed")
        await callback.message.answer(caption, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data == "menu:portfolio")
async def open_portfolio(callback: CallbackQuery) -> None:
    await show_item(callback, 0)


@router.callback_query(F.data.startswith("portfolio:"))
async def navigate(callback: CallbackQuery) -> None:
    idx = int(callback.data.split(":", 1)[1])
    await show_item(callback, idx)
