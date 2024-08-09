from logging.handlers import RotatingFileHandler
import sys

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from bot.enums import Stage


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    ADMIN: int
    TABLE_NAME: str
    STAGE: Stage
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_USER: str
    POSTGRES_DB: str
    echo: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    @property
    def get_db_connection_string(self):
        return SecretStr(
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD.get_secret_value()}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

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
