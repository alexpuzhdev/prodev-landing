import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from . import config, keyboards, screen
from .backend import backend
from .menu import FALLBACK_ERROR, texts

router = Router()
log = logging.getLogger(__name__)

TYPE_LABELS = {
    "mvp": "MVP",
    "landing": "Лендинг",
    "webapp": "Веб-приложение",
    "support": "Поддержка",
}


class LeadForm(StatesGroup):
    task = State()
    project_type = State()
    timeline = State()
    confirm = State()


async def ask_task(bot: Bot, chat_id: int, state: FSMContext, t: dict[str, str]) -> None:
    await state.set_state(LeadForm.task)
    await screen.show_banner(bot, chat_id, state, "contact", t["botLeadAskTask"],
                             keyboards.back_menu(t))


async def ask_type(bot: Bot, chat_id: int, state: FSMContext, t: dict[str, str]) -> None:
    await state.set_state(LeadForm.project_type)
    await screen.show_banner(bot, chat_id, state, "contact", t["botLeadAskType"],
                             keyboards.lead_types(t))


async def ask_timeline(bot: Bot, chat_id: int, state: FSMContext, t: dict[str, str]) -> None:
    await state.set_state(LeadForm.timeline)
    await screen.show_banner(bot, chat_id, state, "contact", t["botLeadAskTimeline"],
                             keyboards.lead_back_only(t))


async def ask_confirm(bot: Bot, chat_id: int, state: FSMContext, t: dict[str, str]) -> None:
    data = await state.get_data()
    summary = (
        f"{t['botLeadConfirm']}\n\n"
        f"Задача: {data.get('task', '')}\n"
        f"Тип: {TYPE_LABELS.get(data.get('project_type', ''), data.get('project_type', ''))}\n"
        f"Сроки: {data.get('timeline', '')}"
    )
    await state.set_state(LeadForm.confirm)
    await screen.show_banner(bot, chat_id, state, "contact", summary, keyboards.lead_confirm(t))


@router.callback_query(F.data == "menu:lead")
async def start_lead(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        t = await texts()
    except Exception:
        log.exception("backend unavailable on lead start")
        await callback.answer(FALLBACK_ERROR, show_alert=True)
        return
    await ask_task(callback.bot, callback.message.chat.id, state, t)
    await callback.answer()


@router.message(LeadForm.task)
async def got_task(message: Message, state: FSMContext) -> None:
    t = await texts()
    await state.update_data(task=message.text or "")
    await screen.delete_user(message)
    await ask_type(message.bot, message.chat.id, state, t)


@router.callback_query(LeadForm.project_type, F.data.startswith("lead_type:"))
async def got_type(callback: CallbackQuery, state: FSMContext) -> None:
    t = await texts()
    await state.update_data(project_type=callback.data.split(":", 1)[1])
    await ask_timeline(callback.bot, callback.message.chat.id, state, t)
    await callback.answer()


@router.message(LeadForm.timeline)
async def got_timeline(message: Message, state: FSMContext) -> None:
    t = await texts()
    await state.update_data(timeline=message.text or "")
    await screen.delete_user(message)
    await ask_confirm(message.bot, message.chat.id, state, t)


@router.callback_query(LeadForm.project_type, F.data == "lead:back")
async def back_to_task(callback: CallbackQuery, state: FSMContext) -> None:
    t = await texts()
    await ask_task(callback.bot, callback.message.chat.id, state, t)
    await callback.answer()


@router.callback_query(LeadForm.timeline, F.data == "lead:back")
async def back_to_type(callback: CallbackQuery, state: FSMContext) -> None:
    t = await texts()
    await ask_type(callback.bot, callback.message.chat.id, state, t)
    await callback.answer()


@router.callback_query(LeadForm.confirm, F.data == "lead:back")
async def back_to_timeline(callback: CallbackQuery, state: FSMContext) -> None:
    t = await texts()
    await ask_timeline(callback.bot, callback.message.chat.id, state, t)
    await callback.answer()


@router.callback_query(LeadForm.confirm, F.data == "lead:send")
async def send(callback: CallbackQuery, state: FSMContext) -> None:
    t = await texts()
    data = await state.get_data()
    user = callback.from_user
    payload = {
        "tg_user_id": user.id,
        "username": user.username or "",
        "name": user.full_name,
        "task": data["task"],
        "project_type": data["project_type"],
        "timeline": data["timeline"],
    }
    try:
        ok = await backend.create_lead(payload)
    except Exception:
        log.exception("lead create failed")
        ok = False
    if not ok:
        await callback.answer(FALLBACK_ERROR, show_alert=True)
        return
    await screen.exit_flow(state)
    await callback.answer(t["botLeadThanks"], show_alert=True)
    await screen.show_banner(
        callback.bot, callback.message.chat.id, state, "welcome",
        t["botWelcome"], keyboards.main_menu(t),
    )
    if config.OWNER_CHAT_ID:
        contact = f"@{user.username}" if user.username else f"id {user.id}"
        summary = (
            f"Новая заявка\n"
            f"Имя: {user.full_name} ({contact})\n"
            f"Тип: {TYPE_LABELS.get(data['project_type'], data['project_type'])}\n"
            f"Сроки: {data['timeline']}\n\n"
            f"{data['task']}"
        )
        try:
            await callback.bot.send_message(config.OWNER_CHAT_ID, summary)
        except Exception:
            log.exception("owner notify failed")
