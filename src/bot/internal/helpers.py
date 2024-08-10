from bot.internal.enums import Nomination
from bot.internal.lexicon import texts
from database.models import Nominee, User


def voting_available(user: User) -> bool:
    return not all(
        (
            user.voted_1,
            user.voted_2,
            user.voted_3,
            user.voted_4,
            user.voted_5,
            user.voted_6,
            user.voted_7,
            user.voted_8,
        )
    )


def number_to_nomination(number: int) -> str:
    dictionary = {
        1: 'Самый популярный мастер',
        2: 'Лучший бренд материала для плетения',
        3: 'Лучшие украшения и аксессуары для брейдинга',
        4: 'Лучшая косметика для брейдинга',
        5: 'Королева брейдинга',
        6: 'Король брейдинга',
        7: 'Песня года',
        8: 'Видео года',
    }
    return dictionary[number]


async def get_nominees_list(nomination: Nomination, nominees: list[Nominee]) -> str:
    text = f'Номинация: <b>{number_to_nomination(nomination.value)}</b>.\n\n'
    for i, nominee in enumerate(nominees, start=1):
        name = nominee.name + ' ' + nominee.last_name if nominee.last_name else nominee.name
        text += texts['nominee_template'].format(i, name, nominee.link)
    return text
