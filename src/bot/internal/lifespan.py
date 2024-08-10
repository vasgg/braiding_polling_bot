import asyncio
import os

from aiogram import Bot
from asyncio import CancelledError, Queue, Task

from config import settings


async def on_startup(bot: Bot):
    folder = os.path.basename(os.getcwd())
    await bot.send_message(
        settings.ADMIN,
        f'<b>{folder.replace("_", " ")} started</b>\n\n/start',
        disable_notification=True,
    )


async def on_shutdown(bot: Bot, queue: Queue, task: Task, event: asyncio.Event):
    await queue.join()
    event.set()
    await task
    folder = os.path.basename(os.getcwd())
    await bot.send_message(
        settings.ADMIN,
        f'<b>{folder.replace("_", " ")} shutdown</b>',
        disable_notification=True,
    )
