from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from . import config


def _two_columns(buttons: list[InlineKeyboardButton]) -> list[list[InlineKeyboardButton]]:
    return [buttons[i : i + 2] for i in range(0, len(buttons), 2)]


def _with_nav(
    content_rows: list[list[InlineKeyboardButton]],
    t: dict[str, str],
    back_cb: str | None = None,
) -> InlineKeyboardMarkup:
    rows = list(content_rows)
    if back_cb:
        rows.append([InlineKeyboardButton(text=t["botBackStep"], callback_data=back_cb)])
    rows.append([InlineKeyboardButton(text=t["botBack"], callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _with_nav_back_bottom(
    content_rows: list[list[InlineKeyboardButton]],
    t: dict[str, str],
    back_cb: str,
) -> InlineKeyboardMarkup:
    """Анкета: 'В меню' над 'Назад' (шаг назад - самой нижней кнопкой)."""
    rows = list(content_rows)
    rows.append([InlineKeyboardButton(text=t["botBack"], callback_data="menu:main")])
    rows.append([InlineKeyboardButton(text=t["botBackStep"], callback_data=back_cb)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def main_menu(t: dict[str, str]) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=t["botMenuPortfolio"], callback_data="menu:portfolio"),
        InlineKeyboardButton(text=t["botMenuServices"], callback_data="menu:services"),
        InlineKeyboardButton(text=t["botMenuLead"], callback_data="menu:lead"),
        InlineKeyboardButton(text=t["botMenuAbout"], callback_data="menu:about"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=_two_columns(buttons))


def back_menu(t: dict[str, str]) -> InlineKeyboardMarkup:
    return _with_nav([], t)


def services_menu(t: dict[str, str]) -> InlineKeyboardMarkup:
    content = [[InlineKeyboardButton(text=t["botMenuLead"], callback_data="menu:lead")]]
    return _with_nav(content, t)


def about_menu(t: dict[str, str]) -> InlineKeyboardMarkup:
    content = [
        [
            InlineKeyboardButton(text=t["botAboutSite"], url=config.SITE_URL),
            InlineKeyboardButton(text=t["botMenuLead"], callback_data="menu:lead"),
        ]
    ]
    return _with_nav(content, t)


def portfolio_nav(t: dict[str, str], idx: int, total: int) -> InlineKeyboardMarkup:
    row = []
    if idx > 0:
        row.append(InlineKeyboardButton(text="◀", callback_data=f"portfolio:{idx - 1}"))
    row.append(InlineKeyboardButton(text=f"{idx + 1}/{total}", callback_data="noop"))
    if idx < total - 1:
        row.append(InlineKeyboardButton(text="▶", callback_data=f"portfolio:{idx + 1}"))
    return _with_nav([row], t)


def lead_types(t: dict[str, str]) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=t["botLeadTypeMvp"], callback_data="lead_type:mvp"),
        InlineKeyboardButton(text=t["botLeadTypeLanding"], callback_data="lead_type:landing"),
        InlineKeyboardButton(text=t["botLeadTypeWebapp"], callback_data="lead_type:webapp"),
        InlineKeyboardButton(text=t["botLeadTypeSupport"], callback_data="lead_type:support"),
    ]
    return _with_nav_back_bottom(_two_columns(buttons), t, back_cb="lead:back")


def lead_back_only(t: dict[str, str]) -> InlineKeyboardMarkup:
    return _with_nav_back_bottom([], t, back_cb="lead:back")


def lead_confirm(t: dict[str, str]) -> InlineKeyboardMarkup:
    content = [[InlineKeyboardButton(text=t["botLeadSend"], callback_data="lead:send")]]
    return _with_nav_back_bottom(content, t, back_cb="lead:back")
