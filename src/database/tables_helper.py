from sqlalchemy.ext.asyncio import AsyncEngine

from database_connector import DatabaseConnector, get_db
from models import Base, Nominee


async def create_or_drop_db(engine: AsyncEngine, create: bool = True):
    async with engine.begin() as conn:
        if create:
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
        else:
            await conn.run_sync(Base.metadata.drop_all)


async def populate_db(db_connector: DatabaseConnector):
    async with db_connector.session_factory.begin() as db_session:
        for name, lastname, link, nomination in [
            ('Пётр', 'Семенченко', 'https://youtu.be/8EHKcnoCRJM', 6),
            ('Данила', 'Дерябин', '-', 6),
        ]:
            nominee = Nominee(name=name, last_name=lastname, link=link, nomination=nomination)
            db_session.add(nominee)
        await db_session.commit()

if __name__ == '__main__':
    import asyncio

    db = get_db()
    asyncio.run(create_or_drop_db(db.engine))
    # asyncio.run(populate_db(db))
