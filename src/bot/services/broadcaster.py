import asyncio
import logging
from contextlib import suppress

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.crud.user import get_all_users_ids

logger = logging.getLogger(__name__)

_PROGRESS_EVERY = 50
_SEND_DELAY = 0.04
MAX_BROADCAST_LENGTH = 4000


async def _edit(bot: Bot, chat_id: int, message_id: int, text: str) -> None:
    with suppress(TelegramBadRequest):
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)


async def run_broadcast(
    bot: Bot,
    text: str,
    admin_chat_id: int,
    status_message_id: int,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        user_ids = await get_all_users_ids(session)

    total = len(user_ids)
    sent = blocked = failed = 0

    for i, tg_id in enumerate(user_ids, 1):
        try:
            await bot.send_message(tg_id, text, parse_mode=None)
            sent += 1
        except TelegramForbiddenError:
            blocked += 1
        except Exception as e:
            logger.warning('Broadcast failed for %s: %s', tg_id, e)
            failed += 1

        if i % _PROGRESS_EVERY == 0:
            await _edit(
                bot,
                admin_chat_id,
                status_message_id,
                f'Рассылка: {i}/{total}\nОтправлено: {sent}\nЗаблокировали: {blocked}\nОшибок: {failed}',
            )
        await asyncio.sleep(_SEND_DELAY)

    await _edit(
        bot,
        admin_chat_id,
        status_message_id,
        f'Рассылка завершена ({total}/{total}).\nОтправлено: {sent}\nЗаблокировали бота: {blocked}\nОшибок: {failed}',
    )
    logger.info('Broadcast done: total=%d sent=%d blocked=%d failed=%d', total, sent, blocked, failed)
