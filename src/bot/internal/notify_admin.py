import os

from aiogram import Bot

from config import settings


async def on_startup_notify(bot: Bot):
    folder = os.path.basename(os.getcwd())
    await bot.send_message(
        settings.ADMIN,
        f'<b>{folder.replace("_", " ")} started</b>\n\n/start',
        disable_notification=True,
    )


async def on_shutdown_notify(bot: Bot):
    folder = os.path.basename(os.getcwd())
    await bot.send_message(
        settings.ADMIN,
        f'<b>{folder.replace("_", " ")} shutdown</b>',
        disable_notification=True,
    )
