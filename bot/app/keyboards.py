from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from . import config


def main_menu(t: dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["botMenuPortfolio"], callback_data="menu:portfolio")],
            [InlineKeyboardButton(text=t["botMenuServices"], callback_data="menu:services")],
            [InlineKeyboardButton(text=t["botMenuLead"], callback_data="menu:lead")],
            [InlineKeyboardButton(text=t["botMenuAbout"], callback_data="menu:about")],
        ]
    )


def back_menu(t: dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t["botBack"], callback_data="menu:main")]]
    )


def about_menu(t: dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["botAboutSite"], url=config.SITE_URL)],
            [InlineKeyboardButton(text=t["botMenuLead"], callback_data="menu:lead")],
            [InlineKeyboardButton(text=t["botBack"], callback_data="menu:main")],
        ]
    )


def services_menu(t: dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["botMenuLead"], callback_data="menu:lead")],
            [InlineKeyboardButton(text=t["botBack"], callback_data="menu:main")],
        ]
    )


def portfolio_nav(t: dict[str, str], idx: int, total: int) -> InlineKeyboardMarkup:
    nav = []
    if idx > 0:
        nav.append(InlineKeyboardButton(text="<", callback_data=f"portfolio:{idx - 1}"))
    nav.append(InlineKeyboardButton(text=f"{idx + 1}/{total}", callback_data="noop"))
    if idx < total - 1:
        nav.append(InlineKeyboardButton(text=">", callback_data=f"portfolio:{idx + 1}"))
    return InlineKeyboardMarkup(
        inline_keyboard=[nav, [InlineKeyboardButton(text=t["botBack"], callback_data="menu:main")]]
    )


def lead_types(t: dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["botLeadTypeMvp"], callback_data="lead_type:mvp")],
            [InlineKeyboardButton(text=t["botLeadTypeLanding"], callback_data="lead_type:landing")],
            [InlineKeyboardButton(text=t["botLeadTypeWebapp"], callback_data="lead_type:webapp")],
            [InlineKeyboardButton(text=t["botLeadTypeSupport"], callback_data="lead_type:support")],
        ]
    )


def lead_confirm(t: dict[str, str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t["botLeadSend"], callback_data="lead:send"),
                InlineKeyboardButton(text=t["botLeadCancel"], callback_data="lead:cancel"),
            ]
        ]
    )
