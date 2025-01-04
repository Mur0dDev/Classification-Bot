from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery
from loader import dp
from states.classify_state import ClassifyState
from keyboards.inline.choose_type import choose_type_keyboard


@dp.message_handler(Command("classify"))
async def start_classification(message: types.Message):
    """
    Entry point for the /classify command.
    """
    await message.answer("What type of being?", reply_markup=choose_type_keyboard)
    await ClassifyState.choose_type.set()  # Set the state to choose a being type


@dp.callback_query_handler(state=ClassifyState.choose_type)
async def process_choose_type(call: CallbackQuery, state: FSMContext):
    """
    Handle the user's selection of being type.
    """
    choice = call.data
    await call.message.edit_reply_markup()  # Remove inline buttons after selection

    if choice == "human":
        await call.message.answer("You selected: Human. Let's proceed with data collection.")
        # Transition to next state (e.g., Human flow)
        await state.finish()  # Reset state for now (extend later for Human flow)
    elif choice == "animal":
        await call.message.answer("You selected: Animal. Let's proceed with data collection.")
        # Transition to next state (e.g., Animal flow)
        await state.finish()
    elif choice == "alien":
        await call.message.answer("You selected: Alien. Let's proceed with data collection.")
        # Transition to next state (e.g., Alien flow)
        await state.finish()
    else:
        await call.message.answer("Invalid choice. Please use the buttons provided.")
