import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    TEST_DB_URL: str | None = None
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def get_database_url(for_tests: bool = False) -> str:
    """Возвращает URL базы. Для тестов берёт TEST_DB_URL из env, если указан."""
    if for_tests:
        env_override = os.getenv("TEST_DB_URL")
        if env_override:
            return env_override
        if get_settings().TEST_DB_URL:
            return get_settings().TEST_DB_URL
    return get_settings().DB_URL


settings = get_settings()
database_url = settings.DB_URL

print("DB URL =>", settings.DB_URL)
