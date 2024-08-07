from enum import IntEnum, StrEnum, auto


class Stage(StrEnum):
    PROD = auto()
    DEV = auto()


class Nominations(IntEnum):
    MOST_POPULAR_MASTER = auto()
    BEST_BRAIDING_MATERIALS_BRAND = auto()
    BEST_BRAIDING_ACCESSORIES = auto()
    BEST_BRAIDING_COSMETICS = auto()
    BRAIDING_QUEEN = auto()
    BRAIDING_KING = auto()
    SONG_OF_THE_YEAR = auto()
    VIDEO_OF_THE_YEAR = auto()
