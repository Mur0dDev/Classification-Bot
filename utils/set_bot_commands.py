from aiogram import types

async def set_default_commands(dp):
    """
    Set default bot commands.
    """
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Start the bot"),
        types.BotCommand("classify", "Start the classification process"),
        types.BotCommand("help", "Show help information"),
    ])
