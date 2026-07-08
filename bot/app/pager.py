"""Переиспользуемое листание: ряд кнопок [назад][счётчик][вперёд].

На краях стрелка не убирается, а становится неактивной (полая, callback noop),
чтобы блок не прыгал и было видно, что листать дальше некуда.
"""

from aiogram.types import InlineKeyboardButton

PREV_ACTIVE = "◀"
PREV_EDGE = "◁"
NEXT_ACTIVE = "▶"
NEXT_EDGE = "▷"


def clamp(idx: int, total: int) -> int:
    return max(0, min(idx, total - 1))


def nav_row(prefix: str, idx: int, total: int) -> list[InlineKeyboardButton]:
    """Ряд листания для набора из total элементов на позиции idx.

    prefix задаёт неймспейс callback_data (`<prefix>:<idx>`), чтобы один и тот
    же пейджер обслуживал разные списки.
    """
    if idx > 0:
        prev = InlineKeyboardButton(text=PREV_ACTIVE, callback_data=f"{prefix}:{idx - 1}")
    else:
        prev = InlineKeyboardButton(text=PREV_EDGE, callback_data="noop")
    counter = InlineKeyboardButton(text=f"{idx + 1}/{total}", callback_data="noop")
    if idx < total - 1:
        nxt = InlineKeyboardButton(text=NEXT_ACTIVE, callback_data=f"{prefix}:{idx + 1}")
    else:
        nxt = InlineKeyboardButton(text=NEXT_EDGE, callback_data="noop")
    return [prev, counter, nxt]
