from loader import bot, dp
from handlers.users.bot_class import BeingClassifierBot

# Initialize BeingClassifierBot
classifier_bot = BeingClassifierBot(bot, dp)

__all__ = ["classifier_bot"]
