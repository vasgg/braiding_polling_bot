from aiogram.filters.callback_data import CallbackData

from bot.internal.enums import Nomination


class NominationCallback(CallbackData, prefix='nomination'):
    nomination: Nomination


class ToggleNomineeCallback(CallbackData, prefix='toggle'):
    nomination: Nomination
    nominee_id: int


class SubmitVoteCallback(CallbackData, prefix='submit'):
    nomination: Nomination


class BackToNominationsCallback(CallbackData, prefix='back'):
    pass
