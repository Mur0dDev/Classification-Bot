from aiogram import executor
from loader import dp
from bot_init import classifier_bot
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands

async def on_startup(dispatcher):
    """
    Perform actions at bot startup.
    """
    # Set default bot commands
    await set_default_commands(dispatcher)

    # Notify admins about bot startup
    await on_startup_notify(dispatcher)

    # Register handlers through BeingClassifierBot
    classifier_bot.register_handlers()

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
