from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data import config

# Initialize bot with token
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

# Initialize dispatcher
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
