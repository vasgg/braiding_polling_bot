import logging

import gspread
from sqlalchemy.ext.asyncio import AsyncSession

from bot.internal.helpers import number_to_nomination
from config import settings
from database.crud.nominee import get_nominee
from database.crud.user import get_user_by_id
from database.models import Vote

logger = logging.getLogger(__name__)


async def create_new_vote_record_gsheet(vote: Vote, client: gspread.Client, db_session: AsyncSession):
    spreadsheet = client.open(settings.TABLE_NAME)
    nomination = number_to_nomination(vote.nomination)
    worksheet = spreadsheet.worksheet(nomination)
    user = await get_user_by_id(vote.user_id, db_session)
    nominee = await get_nominee(vote.vote_for, db_session)
    username = '@' + user.username if user.username else ''
    nominee_name = nominee.name + ' ' + nominee.last_name if nominee.last_name else nominee.name
    data = [
        user.fullname,
        vote.user_id,
        username,
        user.phone_number,
        nominee_name,
        vote.vote_for,
        vote.created_at.strftime("%d.%m.%Y"),
    ]
    worksheet.append_row(data)
    logger.info(f"New vote added to {nomination} list: {data}")
