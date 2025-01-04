from difflib import get_close_matches
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from data.predefined_lists import animals
from states.classify_state import ClassifyAnimalState

@dp.message_handler(state=ClassifyAnimalState.species)
async def process_animal_species(message: types.Message, state: FSMContext):
    """
    Process the species input.
    """
    input_text = message.text.strip()

    # Validate if the input is purely text
    if not input_text.isalpha():
        await message.answer("Invalid input. Please provide a valid text-only species (e.g., Dog, Cat).")
        return

    # Capitalize the input and search for similar animals
    species = input_text.capitalize()
    similar_animals = get_close_matches(species, animals, n=10, cutoff=0.4)

    if not similar_animals:
        await message.answer("No similar animals found. Please try again with a different input.")
        return

    # Create an inline keyboard with a maximum of 5 buttons per row
    keyboard = InlineKeyboardMarkup(row_width=5)
    for i, name in enumerate(similar_animals):
        keyboard.insert(InlineKeyboardButton(text=f"{i + 1}", callback_data=f"animal_{i}"))
    keyboard.add(InlineKeyboardButton(text="🔄 Reenter", callback_data="reenter_species"))

    # Send the message with the results and buttons
    results = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(similar_animals)])
    await message.answer(
        f"Did you mean one of these animals?\n\n{results}\n\n"
        "Please select one using the buttons below:",
        reply_markup=keyboard
    )
    await ClassifyAnimalState.species.set()

    # Store the similar animals in FSMContext
    await state.update_data(similar_animals=similar_animals)


@dp.message_handler(state=ClassifyAnimalState.species)
async def process_animal_species_repeat(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer("✨ You have to choose and click from the 🔢 number(s) above\nor you have to click 🔄 Reenter to edit your entry 📝")


@dp.callback_query_handler(lambda call: call.data.startswith("animal_"), state=ClassifyAnimalState.species)
async def process_animal_selection(call: CallbackQuery, state: FSMContext):
    """
    Process the user's selection of an animal from the inline buttons.
    """
    data = await state.get_data()
    similar_animals = data.get("similar_animals")

    # Extract the selected index from the callback data
    selected_index = int(call.data.split("_")[1])
    selected_species = similar_animals[selected_index]

    # Update the state with the selected species
    await state.update_data(species=selected_species)

    # Acknowledge the selection and move to the next step
    await call.message.edit_text(f"Species selected: {selected_species}")
    await call.answer()
    await call.message.answer("🦘 Is this a mammal? (Yes/No):")
    await ClassifyAnimalState.mammal.set()


@dp.callback_query_handler(lambda call: call.data == "reenter_species", state=ClassifyAnimalState.species)
async def process_animal_reenter(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to reenter the species if they click the Reenter button.
    """
    await ClassifyAnimalState.species.set()
    await call.message.edit_text("Please provide the species again:")
    await call.answer()
