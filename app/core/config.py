from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    telegram_token: str

settings = Settings()
