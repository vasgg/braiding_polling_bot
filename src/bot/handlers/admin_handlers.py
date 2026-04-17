import asyncio
import logging
import tempfile
from pathlib import Path

from aiogram import Bot, Router, types
from aiogram.filters import Command
from openpyxl import Workbook
from openpyxl.styles import Font
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from bot.filters.admin import AdminFilter
from bot.internal.helpers import number_to_nomination
from bot.services.broadcaster import MAX_BROADCAST_LENGTH, run_broadcast
from database.crud.user import get_all_users_ids
from database.database_connector import DatabaseConnector
from database.models import Nominee, User, Vote

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command('export'), AdminFilter())
async def export_handler(message: types.Message, db_session: AsyncSession) -> None:
    status = await message.answer('Формирую отчёт...')

    N1 = aliased(Nominee, name='n1')
    N2 = aliased(Nominee, name='n2')
    N3 = aliased(Nominee, name='n3')

    stmt = (
        select(Vote, User, N1, N2, N3)
        .join(User, Vote.user_id == User.id)
        .join(N1, Vote.vote_for_1 == N1.id)
        .join(N2, Vote.vote_for_2 == N2.id)
        .join(N3, Vote.vote_for_3 == N3.id)
        .order_by(Vote.nomination, Vote.created_at)
    )
    result = await db_session.execute(stmt)
    rows = result.all()

    wb = Workbook()
    ws = wb.active
    ws.title = 'Все голоса'

    headers = ['Имя', 'Телефон', 'Номинация', 'Номинант 1', 'Номинант 2', 'Номинант 3', 'Дата и время']
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    def nominee_full_name(n: Nominee) -> str:
        return (n.name + ' ' + n.last_name) if n.last_name else n.name

    for vote, user, n1, n2, n3 in rows:
        ws.append(
            [
                user.fullname,
                user.phone_number or '',
                number_to_nomination(vote.nomination.value),
                nominee_full_name(n1),
                nominee_full_name(n2),
                nominee_full_name(n3),
                vote.created_at.strftime('%d.%m.%Y %H:%M:%S'),
            ]
        )

    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        tmp_path = Path(tmp.name)

    wb.save(tmp_path)

    try:
        await message.answer_document(
            document=types.FSInputFile(tmp_path, filename='braiding_votes_2026.xlsx'),
            caption=f'Голосов: {len(rows)}',
        )
    finally:
        tmp_path.unlink(missing_ok=True)
        await status.delete()


@router.message(Command('broadcast'), AdminFilter())
async def broadcast_handler(
    message: types.Message,
    bot: Bot,
    db_session: AsyncSession,
    db: DatabaseConnector,
) -> None:
    raw = message.text or ''
    parts = raw.split(maxsplit=1)
    text = parts[1].strip() if len(parts) > 1 else ''

    if not text:
        await message.answer('Использование: /broadcast <текст>')
        return

    if len(text) > MAX_BROADCAST_LENGTH:
        await message.answer(f'Сообщение слишком длинное: {len(text)} > {MAX_BROADCAST_LENGTH} символов.')
        return

    total = len(await get_all_users_ids(db_session))
    status = await message.answer(f'Рассылка запущена для {total} пользователей...')

    asyncio.create_task(
        run_broadcast(
            bot=bot,
            text=text,
            admin_chat_id=message.chat.id,
            status_message_id=status.message_id,
            session_factory=db.session_factory,
        ),
    )
