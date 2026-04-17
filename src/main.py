import asyncio
import functools
import logging.config
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from bot.handlers.admin_handlers import router as admin_router
from bot.handlers.base_handlers import router as base_router
from bot.handlers.errors_handler import router as errors_router
from bot.internal.commands import set_bot_commands
from bot.internal.lifespan import on_shutdown, on_startup
from bot.middlewares.auth_middleware import AuthMiddleware
from bot.middlewares.session_middleware import DBSessionMiddleware
from bot.middlewares.updates_dumper_middleware import UpdatesDumperMiddleware
from config import get_logging_config, settings
from database.database_connector import get_db


async def main() -> None:
    logs_directory = Path('logs')
    logs_directory.mkdir(parents=True, exist_ok=True)
    logging_config = get_logging_config('braiding_bot')
    logging.config.dictConfig(logging_config)

    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    db = get_db(settings)
    storage = RedisStorage.from_url(settings.REDIS_DSN)

    dispatcher = Dispatcher(storage=storage)
    db_session_middleware = DBSessionMiddleware(db)
    dispatcher.message.middleware(db_session_middleware)
    dispatcher.callback_query.middleware(db_session_middleware)
    dispatcher.message.middleware(AuthMiddleware())
    dispatcher.callback_query.middleware(AuthMiddleware())
    dispatcher.update.outer_middleware(UpdatesDumperMiddleware())
    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(functools.partial(on_shutdown, bot, db))
    dispatcher.startup.register(functools.partial(set_bot_commands, admin_ids=settings.ADMINS))
    dispatcher.include_routers(admin_router, base_router, errors_router)
    await dispatcher.start_polling(bot)
    logging.info('braiding bot started')


def run_main() -> None:
    asyncio.run(main())


if __name__ == '__main__':
    run_main()
