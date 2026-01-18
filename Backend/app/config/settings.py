# Application configuration settings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_host: str = Field(..., alias="DB_HOST")
    db_port: int = Field(3306, alias="DB_PORT")
    db_name: str = Field(..., alias="DB_NAME")
    callback_timeout: float = Field(5.0, alias="CALLBACK_TIMEOUT")
    max_callback_retries: int = Field(3, alias="MAX_CALLBACK_RETRIES")
    max_workers: int = Field(2, alias="MAX_WORKERS")

    @property
    def database_url(self) -> str:
        """Async database URL for application runtime (aiomysql)"""
        return (
            f"mysql+aiomysql://"
            f"{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    @property
    def database_url_sync(self) -> str:
        """Sync database URL for Alembic migrations (pymysql)"""
        return (
            f"mysql+pymysql://"
            f"{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )