import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from config import settings
from database.database_connector import get_db
from database.models import Base, Nominee


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
        ('Ксения', 'Панда', 'https://youtu.be/7V-E4CcpB8A', 1),
        ('Ида от Afromari', None, 'https://youtube.com/shorts/ZXS9jVzEBow', 2),
        ('Kami-Kami', None, '', 2),
        ('Vera', 'Kudri', 'https://youtu.be/Ira7kgLmIPQ', 2),
        ('WOWbraids', None, 'https://youtu.be/WVOgcmZHx4o', 2),
        ('WowAfroShop', None, '-', 2),
        ('KudriShop', None, 'https://youtu.be/kjhPshzaqrA', 2),
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
        ('Косметика от Afromari', None, 'https://youtu.be/lg41RY6KyQw', 4),
        ('Braids Kos', None, 'https://youtu.be/XEtFQ69oaIY', 4),
        ('Анна', 'Тимичёва', 'https://youtu.be/ZHGXWWlbWik', 5),
        ('Кристина', 'Черныш', 'https://youtu.be/TKWg97L8cjY', 5),
        ('Ксения', 'Панда', '-', 5),
        ('Анастасия', 'Волна', 'https://youtu.be/sVRwQWvTuiM', 5),
        ('Ника', 'Енот', 'https://youtu.be/jdyVq5eKD0E', 5),
        ('Ксения', 'Черёмуха', 'https://youtu.be/777wSNKZ4nw', 5),
        ('Анастасия', 'Десятникова', 'https://youtu.be/iEzTG7vPT6I', 5),
        ('Юлия', 'Батонова', 'https://youtu.be/2OeAYwb_lzQ', 5),
        ('Евгения', 'Исаева', 'https://youtu.be/bBHyICpr07o', 5),
        ('Пётр', 'Семенченко', 'https://youtu.be/8EHKcnoCRJM', 6),
        ('Данила', 'Дерябин', '-', 6),
        ('Анастасия', 'Данилова (Растамама)', 'https://youtu.be/FNvj68ElFak', 7),
        ('Девочки из MintMind - Районы-кварталы', None, 'https://drive.google.com/file/d/1uQBs6p0Q_W7GIqZg3xjCyz0YriakNffp/view?usp=sharing', 7),
        ('Девочки из MintMind - Кукла колдуна', None, 'https://drive.google.com/file/d/1uULeSkcAEAJ7s1yPuC4iNLP4M5AZj8Xa/view?usp=sharing', 7),
        ('Ксения Тюменцева и Оксана Мисюченко', None, 'https://youtu.be/L62TsfPfNRs', 7),
        ('Лосева Мария и Иванова Лилия', None, 'https://drive.google.com/file/d/1qXuo_2-6Tnxkd-KtSp_3PgAF-CUmg3Lc/view?usp=sharing', 7),
        ('Елена', 'Игонина', 'https://www.instagram.com/reel/C8M60tTteRB/?igsh=MWRjcHo4bWN2djJrbQ==', 8),
        ('Юлия', 'Сolosyuliya', 'http://vk.com/clip-184829628_456239118?c=1', 8),
        ('Студия Енот', None, 'https://www.instagram.com/reel/CwC7af0IpSI/?igsh=emF4a20xaXNoODl4', 8),
        ('Екатерина', 'Бурая', 'https://disk.yandex.ru/i/__7pzfkj1UqclQ', 8),
        ('Студия MintMind', None, 'https://www.instagram.com/reel/C3umQOLI5n4/?igsh=MTF4c3dzZnV0eXc4aA==', 8),
        ('Ксения', 'Панда', 'https://www.instagram.com/reel/Cy7pzmvM4Yq/?igsh=MnFnYnMzc2tiMGh1', 8),
        ('Юлия', 'Батонова', 'https://www.instagram.com/reel/C7irnA3NK3e/?igsh=djQzMXAzN3M5dDUy', 8),
        ('Мария', 'Астапушкина', 'https://www.instagram.com/reel/CrvnbILN4-o/?igsh=Zml3bXFjMnJ4dDY0', 8),
        ('Янесса ', None, 'https://www.instagram.com/reel/C2w9PwTMkB_/?igsh=MWNvNjdiMnM3YTIzbQ==', 8),
        ('Лилия', None, 'https://www.instagram.com/reel/Cw25loCsKXM/?igsh=NXJyeXF2NjVndnh2', 8),
        ('Таня', 'Топалова', 'https://www.instagram.com/reel/C8L8l8zs46B/?igsh=MXI2bmphdmFmbWU5OA==', 8),
    ]:
        nominee = Nominee(name=name, last_name=lastname, link=link, nomination=nomination)
        db_session.add(nominee)
    await db_session.commit()


async def main():
    db = get_db(settings)
    await create_or_drop_db(db.engine, False)
    await create_or_drop_db(db.engine)
    async with db.session_factory.begin() as session:
        await populate_db(session)


def run_main():
    asyncio.run(main())


if __name__ == '__main__':
    run_main()
