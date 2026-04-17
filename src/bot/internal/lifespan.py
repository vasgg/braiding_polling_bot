import logging
import os
from contextlib import suppress

from aiogram import Bot

from config import settings
from database.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    folder = os.path.basename(os.getcwd())
    with suppress(Exception):
        await bot.send_message(
            settings.primary_admin,
            f'<b>{folder.replace("_", " ")} started</b>\n\n/start',
            disable_notification=True,
        )


async def on_shutdown(bot: Bot, db: DatabaseConnector) -> None:
    folder = os.path.basename(os.getcwd())
    with suppress(Exception):
        await bot.send_message(
            settings.primary_admin,
            f'<b>{folder.replace("_", " ")} shutdown</b>',
            disable_notification=True,
        )
    try:
        await db.dispose()
    except Exception:
        logger.exception('Failed to dispose db engine on shutdown')
