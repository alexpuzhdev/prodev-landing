import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from . import banners, keyboards
from .backend import backend

router = Router()
log = logging.getLogger(__name__)

KEYS = [
    "botWelcome", "botMenuPortfolio", "botMenuServices", "botMenuLead", "botMenuAbout",
    "botBack", "botPortfolioEmpty", "botAboutSite", "botLeadAskTask", "botLeadAskType",
    "botLeadTypeMvp", "botLeadTypeLanding", "botLeadTypeWebapp", "botLeadTypeSupport",
    "botLeadAskTimeline", "botLeadConfirm", "botLeadSend", "botLeadCancel",
    "botLeadThanks", "botLeadCancelled", "botError",
    "svc1Title", "svc1Text", "svc2Title", "svc2Text",
    "svc3Title", "svc3Text", "svc4Title", "svc4Text",
    "aboutTitle", "aboutP1", "aboutP2",
]

FALLBACK_ERROR = "Сервис временно недоступен, попробуйте позже."


async def texts() -> dict[str, str]:
    data = await backend.texts()
    result = {}
    for key in KEYS:
        row = data.get(key) or {}
        result[key] = row.get("ru") or key
    return result


async def show_main(message: Message) -> None:
    t = await texts()
    await banners.send(message, "welcome", t["botWelcome"], keyboards.main_menu(t))


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    try:
        await show_main(message)
    except Exception:
        log.exception("backend unavailable on start")
        await message.answer(FALLBACK_ERROR)


@router.callback_query(F.data == "menu:main")
async def to_main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    try:
        await show_main(callback.message)
    except Exception:
        log.exception("backend unavailable on menu")
        await callback.message.answer(FALLBACK_ERROR)
    await callback.answer()


@router.callback_query(F.data == "menu:services")
async def services(callback: CallbackQuery) -> None:
    try:
        t = await texts()
    except Exception:
        log.exception("backend unavailable on services")
        await callback.answer(FALLBACK_ERROR, show_alert=True)
        return
    lines = [f"<b>{t[f'svc{i}Title']}</b>\n{t[f'svc{i}Text']}" for i in (1, 2, 3, 4)]
    caption = "\n\n".join(lines)
    await banners.send(callback.message, "services", caption, keyboards.services_menu(t))
    await callback.answer()


@router.callback_query(F.data == "menu:about")
async def about(callback: CallbackQuery) -> None:
    try:
        t = await texts()
    except Exception:
        log.exception("backend unavailable on about")
        await callback.answer(FALLBACK_ERROR, show_alert=True)
        return
    caption = f"<b>{t['aboutTitle']}</b>\n\n{t['aboutP1']}\n\n{t['aboutP2']}"
    await banners.send(callback.message, "about", caption, keyboards.about_menu(t))
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery) -> None:
    await callback.answer()
