from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Nominee


async def get_nominees(nomination_id: int, db_session: AsyncSession) -> list[Nominee]:
    query = select(Nominee).filter(Nominee.nomination == nomination_id)
    result = await db_session.execute(query)
    return list(result.scalars().all())


async def get_nominee(nominee_id: int, db_session: AsyncSession) -> Nominee:
    query = select(Nominee).filter(Nominee.id == nominee_id)
    result = await db_session.execute(query)
    return result.scalar()
