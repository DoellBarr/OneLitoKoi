import configs
from aiogram import Bot
from aiogram.enums import ParseMode


bot = Bot(token=configs.bot_token, parse_mode=ParseMode.MARKDOWN)
