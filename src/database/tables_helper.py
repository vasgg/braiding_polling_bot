import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from models import Base, Nominee


async def create_or_drop_db(engine: AsyncEngine, create: bool = True):
    async with engine.begin() as conn:
        if create:
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
        else:
            await conn.run_sync(Base.metadata.drop_all)


async def populate_db(db_session: AsyncSession):
    for name, lastname, link, nomination in [
        ('Пётр', 'Семенченко', 'https://youtu.be/_EArb1nkjNI', 1),
        ('Анна', 'Тимичёва', 'https://youtu.be/kmEDZG4oaOM', 1),
        ('Мария', 'Астапушкина', 'https://youtu.be/y4tn0UeXWgU', 1),
        ('Евгения', 'Исаева', 'https://youtu.be/uZ3j4L_nG7Y', 1),
        ('Ника', 'Енот', 'https://youtube.com/shorts/OVHLyVFh6pQ?feature=share', 1),
        ('Ольга', 'Оликова', 'https://youtu.be/LfaWRt5XpLs', 1),
        ('Анастасия', 'Волна', 'https://youtu.be/pLFYCIqhU0A', 1),
        ('Тина', 'Паникар', '-', 1),
        ('Юлия', 'Батонова', 'https://youtu.be/YZLsw5st4N8', 1),
        ('Ксения', 'Панда', '-', 1),
        ('Ида от Afromari', None, '-', 2),
        ('Kami-Kami', None, '-', 2),
        ('Vera', 'Kudri', 'https://youtu.be/Ira7kgLmIPQ', 2),
        ('WOWbraids', None, 'https://youtu.be/WVOgcmZHx4o', 2),
        ('WowAfroShop', None, '-', 2),
        ('KudriShop', None, '-', 2),
        ('Easy Shop', None, 'https://youtu.be/jVfjWrwFoXM', 2),
        ('Braids Market', None, 'https://youtu.be/ZnaSEIKftko', 2),
        ('Jolly', None, 'https://youtu.be/g88KhPpxPlQ', 2),
        ('BraidsZver', None, 'https://youtu.be/sA0YbWx6kME', 3),
        ('Flexipin', None, 'https://youtu.be/UEvOuD0MHug', 3),
        ('Студия TopDread', None, 'https://youtu.be/T7gRUV2DJ14', 3),
        ('Banana Caps', None, 'https://youtu.be/b7E2HbTGmG4', 3),
        ('Absolem_crafts', None, 'https://youtu.be/ixZ6E1twREc', 3),
        ('Кристина', 'Москалёва', 'https://youtu.be/qD3ln1Xr2NY', 3),
        ('Clear Braids', None, 'https://youtu.be/5882pezFKys', 4),
        ('Косметика от Afromari', None, '-', 4),
        ('Inday & ArtStu10', None, '-', 4),
        ('Braids Kos', None, 'https://youtu.be/XEtFQ69oaIY', 4),
        ('Анна', 'Тимичёва', 'https://youtu.be/ZHGXWWlbWik', 5),
        ('Кристина', 'Черныш', 'https://youtu.be/TKWg97L8cjY', 5),
        ('Ксения', 'Панда', '-', 5),
        ('Елена', 'Игонина', '-', 5),
        ('Анастасия', 'Волна', 'https://youtu.be/sVRwQWvTuiM', 5),
        ('Анастасия', 'Будыльская', '-', 5),
        ('Ника', 'Енот', 'https://youtu.be/jdyVq5eKD0E', 5),
        ('Анастасия', 'Данилова', '-', 5),
        ('Ксения', 'Черёмуха', '-', 5),
        ('Анастасия', 'Десятникова', 'https://youtu.be/djt4DWbPsY8', 5),
        ('Юлия', 'Батонова', '-', 5),
        ('Евгения', 'Исаева', 'https://youtu.be/bBHyICpr07o', 5),
        ('Пётр', 'Семенченко', 'https://youtu.be/8EHKcnoCRJM', 6),
        ('Данила', 'Дерябин', '-', 6),
    ]:
        nominee = Nominee(name=name, last_name=lastname, link=link, nomination=nomination)
        db_session.add(nominee)
    await db_session.commit()


async def main():
    ...
    # db = get_db(settings)
    # async with db.session_factory.begin() as session:
    #     await populate_db(session)


if __name__ == '__main__':
    asyncio.run(main())
