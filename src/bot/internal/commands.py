from aiogram import Bot, types

default_commands = [
    types.BotCommand(command='/start', description='Главное меню'),
]

admin_commands = [
    types.BotCommand(command='/start', description='Главное меню'),
    types.BotCommand(command='/export', description='Выгрузить голоса в xlsx'),
    types.BotCommand(command='/broadcast', description='Рассылка всем пользователям'),
]


async def set_bot_commands(bot: Bot, admin_ids: list[int]) -> None:
    await bot.set_my_commands(default_commands)
    for admin_id in admin_ids:
        await bot.set_my_commands(
            admin_commands,
            scope=types.BotCommandScopeChat(chat_id=admin_id),
        )
