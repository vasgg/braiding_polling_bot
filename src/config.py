import sys
from datetime import datetime
from logging import Formatter
from logging.handlers import RotatingFileHandler

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from bot.internal.enums import Stage


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    ADMINS: list[int]
    STAGE: Stage

    @field_validator('ADMINS', mode='before')
    @classmethod
    def parse_admins(cls, v: str | list) -> list[int]:
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(',') if x.strip()]
        return v

    @property
    def primary_admin(self) -> int:
        return self.ADMINS[0]

    DATABASE_DSN: str
    REDIS_DSN: str
    echo: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False, extra='allow')


settings = Settings()

main_template = {
    'format': '%(asctime)s | %(message)s',
    'datefmt': '%d.%m.%Y %H:%M:%S%z',
}
error_template = {
    'format': '%(asctime)s [%(levelname)8s] [%(module)s:%(funcName)s:%(lineno)d] %(message)s',
    'datefmt': '%d.%m.%Y %H:%M:%S%z',
}


class CustomFormatter(Formatter):
    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created).astimezone()
        if datefmt:
            base_time = ct.strftime('%d.%m.%Y %H:%M:%S')
            msecs = f'{int(record.msecs):03d}'
            tz = ct.strftime('%z')
            return f'{base_time}.{msecs}{tz}'
        return super().formatTime(record, datefmt)


def get_logging_config(app_name: str):
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'main': {
                '()': CustomFormatter,
                'format': main_template['format'],
                'datefmt': main_template['datefmt'],
            },
            'errors': {
                '()': CustomFormatter,
                'format': error_template['format'],
                'datefmt': error_template['datefmt'],
            },
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'main',
                'stream': sys.stdout,
            },
            'stderr': {
                'class': 'logging.StreamHandler',
                'level': 'WARNING',
                'formatter': 'errors',
                'stream': sys.stderr,
            },
            'file': {
                '()': RotatingFileHandler,
                'level': 'INFO',
                'formatter': 'main',
                'filename': f'logs/{app_name}.log',
                'maxBytes': 3000000,
                'backupCount': 3,
                'encoding': 'utf-8',
            },
        },
        'loggers': {
            'root': {
                'level': 'DEBUG',
                'handlers': ['stdout', 'stderr', 'file'],
            },
        },
    }
