from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from config import settings


class AdminFilter(Filter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user is not None and event.from_user.id in settings.ADMINS
