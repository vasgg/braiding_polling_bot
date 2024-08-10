from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.internal.enums import Stage, TaskType
from bot.internal.schemas import CounterTask, TaskModel
from config import settings
from database.crud.user import add_user_to_db, get_user_by_tg_id


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        db_session = data['db_session']
        queue = data['queue']
        user = await get_user_by_tg_id(event.from_user.id, db_session)
        if not user:
            user = await add_user_to_db(event.from_user, db_session)
            if settings.STAGE == Stage.PROD:
                counter_task = CounterTask(counter=user.id)
                task = TaskModel(task_type=TaskType.USER_COUNTER, task_data=counter_task)
                queue.put_nowait(task)
        data['user'] = user
        return await handler(event, data)
