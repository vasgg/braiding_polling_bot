import logging

from aiogram.client.session import aiohttp
import gspread
from sqlalchemy.ext.asyncio import AsyncSession

from bot.internal.helpers import number_to_nomination
from bot.internal.schemas import CounterTask, VoteTask
from config import settings
from database.crud.nominee import get_nominee
from database.crud.user import get_user_by_id

logger = logging.getLogger(__name__)


async def handle_vote_task(task: VoteTask, client: gspread.Client, db_session: AsyncSession):
    spreadsheet = client.open(settings.TABLE_NAME)
    nomination = number_to_nomination(task.nomination.value)
    worksheet = spreadsheet.worksheet(nomination)
    user = await get_user_by_id(task.user_id, db_session)
    nominee = await get_nominee(task.user_vote_for, db_session)
    username = '@' + user.username if user.username else ''
    nominee_name = nominee.name + ' ' + nominee.last_name if nominee.last_name else nominee.name
    data = [
        user.fullname,
        task.user_id,
        username,
        user.phone_number,
        nominee_name,
        task.user_vote_for,
        task.date,
    ]
    worksheet.append_row(data)
    logger.info(f"New vote added to {nomination} list: {data}")


async def handle_counter_task(task: CounterTask, client: gspread.Client):
    spreadsheet = client.open('users_counter')
    worksheet = spreadsheet.worksheet('Bot users')
    worksheet.update([[task.counter]], 'C7')
    logger.info(f"Updated user counter: {task.counter}")
