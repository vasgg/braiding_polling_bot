from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.internal.enums import Nomination
from bot.internal.helpers import number_to_nomination
from bot.internal.lexicon import TICKET_URL
from bot.keyboards.callbacks import (
    BackToNominationsCallback,
    NominationCallback,
    SubmitVoteCallback,
    ToggleNomineeCallback,
)
from database.models import Nominee, User


def contact_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text='Поделиться телефоном', request_contact=True, one_time_keyboard=True)
    return builder.as_markup(resize_keyboard=True)


def nominations_kb(user: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for idx, nomination in enumerate(Nomination, start=1):
        if not getattr(user, f'voted_{idx}'):
            builder.row(
                InlineKeyboardButton(
                    text=number_to_nomination(idx),
                    callback_data=NominationCallback(nomination=nomination).pack(),
                )
            )
    builder.row(InlineKeyboardButton(text='Купить билет на Премию 🎟', url=TICKET_URL))
    return builder.as_markup()


def nominee_checkbox_kb(
    nominees: list[Nominee],
    nomination: Nomination,
    selected_ids: list[int],
) -> InlineKeyboardMarkup:
    all_three_selected = len(selected_ids) == 3
    builder = InlineKeyboardBuilder()
    for nominee in nominees:
        name = nominee.name + ' ' + nominee.last_name if nominee.last_name else nominee.name
        if nominee.id in selected_ids:
            prefix = '🟢 ' if all_three_selected else '🔵 '
            label = prefix + name
        else:
            label = name
        builder.row(
            InlineKeyboardButton(
                text=label,
                callback_data=ToggleNomineeCallback(nomination=nomination, nominee_id=nominee.id).pack(),
            )
        )
    if all_three_selected:
        builder.row(
            InlineKeyboardButton(
                text='Проголосовать ✅',
                callback_data=SubmitVoteCallback(nomination=nomination).pack(),
            )
        )
    builder.row(InlineKeyboardButton(text='◀️ Назад к номинациям', callback_data=BackToNominationsCallback().pack()))
    return builder.as_markup()
