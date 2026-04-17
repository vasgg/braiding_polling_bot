from aiogram.types import User as TelegramUser
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


async def add_user_to_db(user: TelegramUser, db_session: AsyncSession) -> User:
    stmt = (
        pg_insert(User)
        .values(
            telegram_id=user.id,
            fullname=user.full_name,
            username=user.username,
        )
        .on_conflict_do_nothing(index_elements=['telegram_id'])
    )
    await db_session.execute(stmt)
    await db_session.flush()
    result = await db_session.execute(select(User).filter(User.telegram_id == user.id))
    return result.scalar_one()


async def get_user_by_tg_id(telegram_id: int, db_session: AsyncSession) -> User | None:
    query = select(User).filter(User.telegram_id == telegram_id)
    result = await db_session.execute(query)
    return result.scalar()


async def get_user_by_id(user_id: int, db_session: AsyncSession) -> User | None:
    query = select(User).filter(User.id == user_id)
    result = await db_session.execute(query)
    return result.scalar()


async def get_all_users_ids(db_session: AsyncSession) -> list[int]:
    query = select(User.telegram_id)
    result = await db_session.execute(query)
    return list(result.scalars().all())
