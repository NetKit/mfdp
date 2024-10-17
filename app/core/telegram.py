from app.core import settings

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    settings.telegram_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
