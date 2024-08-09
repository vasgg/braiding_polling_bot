
from logging.handlers import RotatingFileHandler
import sys

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from bot.enums import Stage


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    NGROK_URL: SecretStr
    NGROK_USER: SecretStr
    NGROK_PASS: SecretStr
    TABLE_NAME: str
    ADMIN: int
    DB_NAME: str
    STAGE: Stage
    db_echo: bool = False

    @property
    def aiosqlite_db_url(self) -> str:
        return f'sqlite+aiosqlite:///{self.DB_NAME}.db'

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False, extra='allow')


settings = Settings()


def get_logging_config(app_name: str):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "main": {
                "format": "%(asctime)s.%(msecs)03d [%(levelname)8s] [%(module)s:%(funcName)s:%(lineno)d] %(message)s",
                "datefmt": "%d.%m.%Y %H:%M:%S%z",
            },
            "errors": {
                "format": "%(asctime)s.%(msecs)03d [%(levelname)8s] [%(module)s:%(funcName)s:%(lineno)d] %(message)s",
                "datefmt": "%d.%m.%Y %H:%M:%S%z",
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "main",
                "stream": sys.stdout,
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "level": "WARNING",
                "formatter": "errors",
                "stream": sys.stderr,
            },
            "file": {
                "()": RotatingFileHandler,
                "level": "INFO",
                "formatter": "main",
                "filename": f"logs/{app_name}_log.log",
                "maxBytes": 500000,
                "backupCount": 3,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "root": {
                "level": "DEBUG",
                "handlers": ["stdout", "stderr", "file"],
            },
        },
    }
