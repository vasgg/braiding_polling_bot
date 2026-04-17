import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from config import settings
from database.database_connector import get_db
from database.models import Base, Nominee


async def create_or_drop_db(engine: AsyncEngine, create: bool = True) -> None:
    async with engine.begin() as conn:
        if create:
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
        else:
            await conn.run_sync(Base.metadata.drop_all)


async def populate_db(db_session: AsyncSession) -> None:
    # TODO: replace all placeholder data with real 2026 nominees from client
    # Format: (name, last_name | None, link, nomination_number)
    nominees_data: list[tuple[str, str | None, str, int]] = [
        # Номинация 1 — Самый популярный мастер
        ('Анна', 'Иванова', 'https://youtu.be/abc', 1),
        ('Пётр', 'Сидоров', 'https://youtu.be/xyz', 1),
        ('Студия', 'Брейдинг', '-', 1),
        # Nomination 2
        ('Номинант', '2-1', '-', 2),
        ('Номинант', '2-2', '-', 2),
        ('Номинант', '2-3', '-', 2),
        # Nomination 3
        ('Номинант', '3-1', '-', 3),
        ('Номинант', '3-2', '-', 3),
        ('Номинант', '3-3', '-', 3),
        # Nomination 4
        ('Номинант', '4-1', '-', 4),
        ('Номинант', '4-2', '-', 4),
        ('Номинант', '4-3', '-', 4),
        # Nomination 5
        ('Номинант', '5-1', '-', 5),
        ('Номинант', '5-2', '-', 5),
        ('Номинант', '5-3', '-', 5),
        # Nomination 6
        ('Номинант', '6-1', '-', 6),
        ('Номинант', '6-2', '-', 6),
        ('Номинант', '6-3', '-', 6),
        # Nomination 7
        ('Номинант', '7-1', '-', 7),
        ('Номинант', '7-2', '-', 7),
        ('Номинант', '7-3', '-', 7),
        # Nomination 8
        ('Номинант', '8-1', '-', 8),
        ('Номинант', '8-2', '-', 8),
        ('Номинант', '8-3', '-', 8),
        # Nomination 9
        ('Номинант', '9-1', '-', 9),
        ('Номинант', '9-2', '-', 9),
        ('Номинант', '9-3', '-', 9),
        # Nomination 10
        ('Номинант', '10-1', '-', 10),
        ('Номинант', '10-2', '-', 10),
        ('Номинант', '10-3', '-', 10),
        # Nomination 11
        ('Номинант', '11-1', '-', 11),
        ('Номинант', '11-2', '-', 11),
        ('Номинант', '11-3', '-', 11),
        # Nomination 12
        ('Номинант', '12-1', '-', 12),
        ('Номинант', '12-2', '-', 12),
        ('Номинант', '12-3', '-', 12),
        # Nomination 13
        ('Номинант', '13-1', '-', 13),
        ('Номинант', '13-2', '-', 13),
        ('Номинант', '13-3', '-', 13),
    ]
    for name, lastname, link, nomination in nominees_data:
        nominee = Nominee(name=name, last_name=lastname, link=link, nomination=nomination)
        db_session.add(nominee)
    await db_session.commit()


async def main() -> None:
    db = get_db(settings)
    await create_or_drop_db(db.engine, False)
    await create_or_drop_db(db.engine)
    async with db.session_factory.begin() as session:
        await populate_db(session)


def run_main() -> None:
    asyncio.run(main())


if __name__ == '__main__':
    run_main()
