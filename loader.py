from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data import config

# Initialize bot with token from .env
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

# Initialize memory storage for FSM
storage = MemoryStorage()

# Create dispatcher
dp = Dispatcher(bot, storage=storage)
