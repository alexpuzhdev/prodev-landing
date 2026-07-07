import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from . import banners, config, keyboards
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


@router.callback_query(F.data == "menu:lead")
async def start_lead(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        t = await texts()
    except Exception:
        log.exception("backend unavailable on lead start")
        await callback.answer(FALLBACK_ERROR, show_alert=True)
        return
    await state.set_state(LeadForm.task)
    await banners.send(callback.message, "contact", t["botLeadAskTask"], keyboards.back_menu(t))
    await callback.answer()


@router.message(LeadForm.task)
async def got_task(message: Message, state: FSMContext) -> None:
    t = await texts()
    await state.update_data(task=message.text or "")
    await state.set_state(LeadForm.project_type)
    await message.answer(t["botLeadAskType"], reply_markup=keyboards.lead_types(t))


@router.callback_query(LeadForm.project_type, F.data.startswith("lead_type:"))
async def got_type(callback: CallbackQuery, state: FSMContext) -> None:
    t = await texts()
    await state.update_data(project_type=callback.data.split(":", 1)[1])
    await state.set_state(LeadForm.timeline)
    await callback.message.answer(t["botLeadAskTimeline"])
    await callback.answer()


@router.message(LeadForm.timeline)
async def got_timeline(message: Message, state: FSMContext) -> None:
    t = await texts()
    await state.update_data(timeline=message.text or "")
    data = await state.get_data()
    summary = (
        f"{t['botLeadConfirm']}\n\n"
        f"Задача: {data['task']}\n"
        f"Тип: {TYPE_LABELS.get(data['project_type'], data['project_type'])}\n"
        f"Сроки: {data['timeline']}"
    )
    await state.set_state(LeadForm.confirm)
    await message.answer(summary, reply_markup=keyboards.lead_confirm(t))


@router.callback_query(LeadForm.confirm, F.data == "lead:cancel")
async def cancel(callback: CallbackQuery, state: FSMContext) -> None:
    t = await texts()
    await state.clear()
    await callback.message.answer(t["botLeadCancelled"], reply_markup=keyboards.main_menu(t))
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
    await state.clear()
    await callback.message.answer(t["botLeadThanks"], reply_markup=keyboards.main_menu(t))
    await callback.answer()
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
