import logging
import traceback
import typing

import aiogram
from aiogram import Router

from config import settings

if typing.TYPE_CHECKING:
    from aiogram.types.error_event import ErrorEvent

logger = logging.getLogger(__name__)
router = Router()


@router.errors()
async def error_handler(error_event: 'ErrorEvent', bot: aiogram.Bot) -> None:
    exc_info = error_event.exception
    exc_traceback = ''.join(traceback.format_exception(exc_info))
    tb = exc_traceback[-3500:]

    error_message = (
        f'🚨 <b>An error occurred</b> 🚨\n\n'
        f'<b>Type:</b> {type(exc_info).__name__}\n<b>Message:</b> {exc_info}\n\n'
        f'<b>Traceback:</b>\n<code>{tb}</code>'
    )
    logger.exception('Exception:', exc_info=exc_info)

    try:
        await bot.send_message(settings.primary_admin, error_message)
    except Exception:
        logger.exception('Failed to send error notification to admin')
