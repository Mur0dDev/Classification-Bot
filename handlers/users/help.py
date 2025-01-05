from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp
from filters import IsPrivate

from loader import dp


@dp.message_handler(IsPrivate(), CommandHelp())
async def bot_help(message: types.Message):
    """
    Handles the /help command in private chats and provides a list of commands.
    """
    text = (
        "🤖 *Bot Help Menu*\n",
        "📋 *Commands:*",
        "🔹 /start - Start the bot and receive a welcome message",
        "🔹 /help - Get help and a list of available commands",
        "",
        "⚠️ *The bot operates in the following areas:*",
        "- Classification of human data",
        "- Classification of animal data",
        "- Classification of alien (extra-terrestrial) data",
        "",
        "📞 Need further assistance? Contact the admin."
    )

    await message.answer("\n".join(text), parse_mode="Markdown")
