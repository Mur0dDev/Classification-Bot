from handlers.users.classify import start_classification, process_being_type, process_human_data  # Import existing handlers
from utils.db_api.google_sheets import GoogleSheetsClient  # Import Google Sheets client
from aiogram import Bot, Dispatcher

class BeingClassifierBot:
    def __init__(self, bot: Bot, dp: Dispatcher):
        """
        Initialize the bot, dispatcher, and Google Sheets client.
        :param bot: Aiogram Bot instance.
        :param dp: Aiogram Dispatcher instance.
        """
        self.bot = bot
        self.dp = dp
        self.google_sheets = GoogleSheetsClient(
            credentials_file="credentials.json",
            spreadsheet_name="Being Classification Data"
        )

    def register_handlers(self):
        """
        Register all handlers with the dispatcher.
        """
        # Command handlers
        self.dp.register_message_handler(start_classification, commands=["classify"])

        # Callback query handlers
        self.dp.register_callback_query_handler(process_being_type, lambda call: call.data.startswith("type_"))

        # Example: Add other handlers as needed
        # self.dp.register_message_handler(process_human_data, state=...)

    def save_to_sheets(self, data):
        """
        Save the classified data to Google Sheets.
        :param data: List of data to save.
        """
        self.google_sheets.authenticate()
        self.google_sheets.append_data("Humans", data)

    def post_to_group(self, data):
        """
        Post the classification results to a Telegram group.
        :param data: Data to format and post.
        """
        # Placeholder for posting data to a Telegram group
        pass
