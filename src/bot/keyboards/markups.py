from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.internal.enums import Action, Nomination
from bot.internal.helpers import number_to_nomination
from bot.keyboards.callbacks import NominationCallback, NomineeCallback, VoteConfirmationCallback
from database.models import Nominee, User


def contact_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text='Поделиться телефоном', request_contact=True, one_time_keyboard=True)
    return builder.as_markup(resize_keyboard=True)


def nominations_kb(user: User) -> InlineKeyboardMarkup:
    vote_attributes = [
        user.voted_1,
        user.voted_2,
        user.voted_3,
        user.voted_4,
        user.voted_5,
        user.voted_6,
        user.voted_7,
        user.voted_8
    ]
    builder = InlineKeyboardBuilder()
    for idx, nomination in enumerate(Nomination, start=1):
        if not vote_attributes[idx - 1]:
            builder.row(
                InlineKeyboardButton(
                    text=number_to_nomination(idx), callback_data=NominationCallback(nomination=nomination).pack()
                )
            )
    return builder.as_markup()


def nominee_kb(nominees: list[Nominee]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for nominee in nominees:
        builder.row(
            InlineKeyboardButton(
                text=nominee.name + ' ' + nominee.last_name if nominee.last_name else nominee.name,
                callback_data=NomineeCallback(nomination=nominee.nomination, nominee_id=nominee.id).pack(),
            )
        )
    return builder.as_markup()


def vote_confirmation_kb(nomination: Nomination, nominee_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='Да',
            callback_data=VoteConfirmationCallback(
                action=Action.VOTE, nomination=nomination, nominee_id=nominee_id
            ).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text='Назад',
            callback_data=VoteConfirmationCallback(
                action=Action.BACK,
                nomination=nomination,
            ).pack(),
        )
    )
    return builder.as_markup()
