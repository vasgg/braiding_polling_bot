import asyncio
import functools
import logging.config
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from bot.handlers.base_handlers import router as base_router
from bot.handlers.errors_handler import router as errors_router
from bot.internal.commands import set_bot_commands
from bot.internal.lifespan import on_shutdown, on_startup
from bot.middlewares.auth_middleware import AuthMiddleware
from bot.middlewares.session_middleware import DBSessionMiddleware
from bot.middlewares.updates_dumper_middleware import UpdatesDumperMiddleware
from config import get_logging_config, settings
from database.database_connector import get_db
from worker import worker


async def main():
    logs_directory = Path("logs")
    logs_directory.mkdir(parents=True, exist_ok=True)
    logging_config = get_logging_config(__name__)
    logging.config.dictConfig(logging_config)

    bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    db = get_db(settings)
    storage = MemoryStorage()

    queue = asyncio.Queue(maxsize=35)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(credentials)

    event = asyncio.Event()
    task = asyncio.create_task(worker(queue, client, event, db))

    dispatcher = Dispatcher(storage=storage, queue=queue, events=event)
    db_session_middleware = DBSessionMiddleware(db)
    dispatcher.message.middleware(db_session_middleware)
    dispatcher.callback_query.middleware(db_session_middleware)
    dispatcher.message.middleware(AuthMiddleware())
    dispatcher.callback_query.middleware(AuthMiddleware())
    dispatcher.update.outer_middleware(UpdatesDumperMiddleware())
    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(functools.partial(on_shutdown, bot, queue, task, event))
    dispatcher.startup.register(set_bot_commands)
    dispatcher.include_routers(base_router, errors_router)
    await dispatcher.start_polling(bot)
    logging.info("bot started")


def run_main():
    asyncio.run(main())


if __name__ == '__main__':
    run_main()
