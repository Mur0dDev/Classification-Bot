from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Inline keyboard for choosing a being type
choose_type_keyboard = InlineKeyboardMarkup(row_width=3)
choose_type_keyboard.add(
    InlineKeyboardButton(text="Human", callback_data="human"),
    InlineKeyboardButton(text="Animal", callback_data="animal"),
    InlineKeyboardButton(text="Alien", callback_data="alien")
)
