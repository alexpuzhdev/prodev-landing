from aiogram.types import FSInputFile, InlineKeyboardMarkup, Message

from . import config

_file_ids: dict[str, str] = {}


async def send(message: Message, name: str, caption: str, markup: InlineKeyboardMarkup) -> None:
    """Отправляет баннер с подписью и клавиатурой, кэшируя file_id после первой загрузки."""
    cached = _file_ids.get(name)
    photo = cached or FSInputFile(config.ASSETS_DIR / f"{name}.png")
    sent = await message.answer_photo(photo, caption=caption, reply_markup=markup)
    if not cached and sent.photo:
        _file_ids[name] = sent.photo[-1].file_id
