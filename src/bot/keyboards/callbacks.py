from aiogram.filters.callback_data import CallbackData

from bot.enums import Action, Nomination


class NominationCallback(CallbackData, prefix='nomination'):
    nomination: Nomination


class NomineeCallback(CallbackData, prefix='nominee'):
    nomination: Nomination
    nominee_id: int


class VoteConfirmationCallback(CallbackData, prefix='vote'):
    action: Action
    nomination: Nomination
    nominee_id: int | None = None
