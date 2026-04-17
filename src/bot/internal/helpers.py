from bot.internal.enums import Nomination
from database.models import User

_NOMINATION_NAMES: dict[int, str] = {
    # TODO: replace placeholders with real 2026 nomination names from client
    1: 'Номинация 1',
    2: 'Номинация 2',
    3: 'Номинация 3',
    4: 'Номинация 4',
    5: 'Номинация 5',
    6: 'Номинация 6',
    7: 'Номинация 7',
    8: 'Номинация 8',
    9: 'Номинация 9',
    10: 'Номинация 10',
    11: 'Номинация 11',
    12: 'Номинация 12',
    13: 'Номинация 13',
}

_NOMINATION_COUNT = len(Nomination)


def voting_available(user: User) -> bool:
    return not all(getattr(user, f'voted_{i}') for i in range(1, _NOMINATION_COUNT + 1))


def number_to_nomination(number: int) -> str:
    return _NOMINATION_NAMES.get(number, f'Номинация {number}')
