"""Единственный экран бота: одно сообщение, которое редактируется по ходу диалога.

Фото и текст нельзя превратить друг в друга редактированием, поэтому при смене
типа экрана старое сообщение удаляется и отправляется новое. В остальных случаях
(фото -> фото, текст -> текст) сообщение правится на месте и не плодится.
"""

import logging

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    FSInputFile,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

from . import config

log = logging.getLogger(__name__)

_photo_cache: dict[str, str] = {}


async def _safe_delete(bot: Bot, chat_id: int, message_id: int) -> None:
    try:
        await bot.delete_message(chat_id, message_id)
    except TelegramBadRequest:
        pass


async def delete_user(message: Message) -> None:
    """Удаляет сообщение пользователя (в приватном чате боту это разрешено)."""
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


async def exit_flow(state: FSMContext) -> None:
    """Выходит из анкеты, сохраняя привязку к текущему экрану бота."""
    data = await state.get_data()
    keep = {k: data[k] for k in ("screen_id", "screen_kind") if k in data}
    await state.set_data(keep)
    await state.set_state(None)


def _remember(cache_key: str, message) -> None:
    if isinstance(message, Message) and message.photo:
        _photo_cache[cache_key] = message.photo[-1].file_id


async def _show_photo(
    bot: Bot,
    chat_id: int,
    state: FSMContext,
    cache_key: str,
    source,
    caption: str,
    markup: InlineKeyboardMarkup,
) -> None:
    data = await state.get_data()
    sid = data.get("screen_id")
    kind = data.get("screen_kind")
    photo = _photo_cache.get(cache_key) or source
    if sid and kind == "photo":
        try:
            edited = await bot.edit_message_media(
                chat_id=chat_id,
                message_id=sid,
                media=InputMediaPhoto(media=photo, caption=caption, parse_mode=ParseMode.HTML),
                reply_markup=markup,
            )
            _remember(cache_key, edited)
            return
        except TelegramBadRequest:
            pass
    if sid:
        await _safe_delete(bot, chat_id, sid)
    sent = await bot.send_photo(chat_id, photo, caption=caption, reply_markup=markup)
    _remember(cache_key, sent)
    await state.update_data(screen_id=sent.message_id, screen_kind="photo")


async def show_banner(
    bot: Bot,
    chat_id: int,
    state: FSMContext,
    name: str,
    caption: str,
    markup: InlineKeyboardMarkup,
) -> None:
    source = FSInputFile(config.ASSETS_DIR / f"{name}.png")
    await _show_photo(bot, chat_id, state, f"banner:{name}", source, caption, markup)


async def show_bytes(
    bot: Bot,
    chat_id: int,
    state: FSMContext,
    cache_key: str,
    data: bytes,
    caption: str,
    markup: InlineKeyboardMarkup,
) -> None:
    source = BufferedInputFile(data, filename="image.png")
    await _show_photo(bot, chat_id, state, f"item:{cache_key}", source, caption, markup)


async def show_text(
    bot: Bot,
    chat_id: int,
    state: FSMContext,
    text: str,
    markup: InlineKeyboardMarkup | None = None,
) -> None:
    data = await state.get_data()
    sid = data.get("screen_id")
    kind = data.get("screen_kind")
    if sid and kind == "text":
        try:
            await bot.edit_message_text(
                text, chat_id=chat_id, message_id=sid, reply_markup=markup
            )
            return
        except TelegramBadRequest:
            pass
    if sid:
        await _safe_delete(bot, chat_id, sid)
    sent = await bot.send_message(chat_id, text, reply_markup=markup)
    await state.update_data(screen_id=sent.message_id, screen_kind="text")
