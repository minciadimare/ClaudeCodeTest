from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./storage/db/armochromia.db"
    storage_path: str = "./storage"
    max_upload_size_mb: int = 10
    debug: bool = False
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "armochromia-scraper/1.0"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
