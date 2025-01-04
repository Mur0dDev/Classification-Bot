from aiogram import types

async def set_default_commands(dp):
    """
    Set default bot commands.
    """
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Start the bot"),
        types.BotCommand("help", "Show help information"),
        types.BotCommand("language", "Set your preferred language (En, Ru, Uz)"),
    ])
