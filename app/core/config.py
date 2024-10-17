from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_name: str
    db_host: str
    database_url: str
    telegram_token: str
    gemini_token: str

settings = Settings()
