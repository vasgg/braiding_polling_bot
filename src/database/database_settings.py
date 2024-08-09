from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    echo: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_USER: str
    POSTGRES_DB: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False, extra='allow')

    @property
    def get_db_connection_string(self):
        return SecretStr(
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD.get_secret_value()}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
