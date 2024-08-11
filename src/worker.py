import asyncio
import logging

import gspread

from bot.internal.enums import TaskType
from bot.internal.gsheets import handle_counter_task, handle_vote_task
from bot.internal.schemas import TaskModel
from database.database_connector import DatabaseConnector

logger = logging.getLogger(__name__)


async def worker(
    queue: asyncio.Queue,
    gspread_client: gspread.Client,
    event: asyncio.Event,
    db: DatabaseConnector
) -> None:
    while event.is_set() is False:
        try:
            try:
                task: TaskModel = await asyncio.wait_for(queue.get(), timeout=1.0)
                queue_len = queue.qsize()
                logger.info(f"Task {task.task_type} ejected from queue. Queue length: {queue_len}")
            except TimeoutError:
                continue
            async with db.session_factory.begin() as db_session:
                match task.task_type:
                    case TaskType.VOTE_LOGGER:
                        await handle_vote_task(task.task_data, gspread_client, db_session)
                    case TaskType.USER_COUNTER:
                        await handle_counter_task(task.task_data, gspread_client)
                    case _:
                        raise AssertionError(f'Unexpected task type {task.type}')
                queue.task_done()
        except Exception as e:
            logger.exception(e)

