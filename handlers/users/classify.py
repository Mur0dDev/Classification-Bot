import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery
from loader import dp
from difflib import get_close_matches
from states.classify_state import ClassifyState
from keyboards.inline.choose_type import choose_type_keyboard
from data.predefined_lists import nationalities, colors
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton




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

    # Handle "Close" button
    if choice == "close":
        await call.message.edit_text("Classification process has been canceled.")
        await state.finish()
        return

    await call.message.edit_reply_markup()  # Remove inline buttons after selection

    if choice == "human":
        await call.message.answer("You selected: 👤 Human. Please provide the gender (Male/Female):")
        await ClassifyState.human_gender.set()  # Transition to the first Human flow state
    elif choice == "animal":
        await call.message.answer("You selected: 🐾 Animal. Let's proceed with data collection.")
        # Transition to the Animal flow (to be added)
        await state.finish()
    elif choice == "alien":
        await call.message.answer("You selected: 👽 Alien. Let's proceed with data collection.")
        # Transition to the Alien flow (to be added)
        await state.finish()
    else:
        await call.message.answer("Invalid choice. Please use the buttons provided.")


@dp.message_handler(state=ClassifyState.human_gender)
async def process_human_gender(message: types.Message, state: FSMContext):
    """
    Process the gender input.
    """
    gender = message.text.strip().capitalize()

    if gender not in ["Male", "Female"]:
        await message.answer("Invalid input. Please enter 'Male' or 'Female'.")
        return

    await state.update_data(gender=gender)
    await message.answer("Great! Now, please provide the age (numeric):")
    await ClassifyState.human_age.set()


@dp.message_handler(state=ClassifyState.human_age)
async def process_human_age(message: types.Message, state: FSMContext):
    """
    Process the age input.
    """
    try:
        age = int(message.text.strip())
        if age <= 0:
            raise ValueError

        await state.update_data(age=age)
        await message.answer("Thank you! Please provide the nationality:")
        await ClassifyState.human_nationality.set()

    except ValueError:
        await message.answer("Invalid input. Age must be a positive number.")





@dp.message_handler(state=ClassifyState.human_nationality)
async def process_human_nationality(message: types.Message, state: FSMContext):
    """
    Process the nationality input.
    """
    input_text = message.text.strip()

    # Validate if the input is purely text
    if not input_text.isalpha():
        await message.answer("Invalid input. Please provide a valid text-only nationality (e.g., American, Uzbek).")
        return

    # Capitalize the input and search for similar nationalities
    nationality = input_text.capitalize()
    similar_nationalities = get_close_matches(nationality, nationalities, n=10, cutoff=0.4)

    if not similar_nationalities:
        await message.answer(
            "No similar nationalities found. Please try again with a different input."
        )
        return

    # Create an inline keyboard with a maximum of 5 buttons per row
    keyboard = InlineKeyboardMarkup(row_width=5)
    for i, name in enumerate(similar_nationalities):
        keyboard.insert(InlineKeyboardButton(text=f"{i + 1}", callback_data=f"nationality_{i}"))
    keyboard.add(InlineKeyboardButton(text="🔄 Reenter", callback_data="reenter"))

    # Send the message with the results and buttons
    results = "\n".join(
        [f"{i + 1}. {name}" for i, name in enumerate(similar_nationalities)]
    )
    await message.answer(
        f"Did you mean one of these nationalities?\n\n{results}\n\n"
        "Please select one using the buttons below:",
        reply_markup=keyboard
    )

    # Store the similar nationalities in FSMContext
    await state.update_data(similar_nationalities=similar_nationalities)

@dp.callback_query_handler(lambda call: call.data.startswith("nationality_"), state=ClassifyState.human_nationality)
async def process_nationality_selection(call: CallbackQuery, state: FSMContext):
    """
    Process the user's selection of nationality from the inline buttons.
    """
    data = await state.get_data()
    similar_nationalities = data.get("similar_nationalities")

    # Extract the selected index from the callback data
    selected_index = int(call.data.split("_")[1])
    selected_nationality = similar_nationalities[selected_index]

    # Update the state with the selected nationality
    await state.update_data(nationality=selected_nationality)

    # Acknowledge the selection and move to the next step
    await call.message.edit_text(f"Nationality selected: {selected_nationality}")
    await call.answer()
    await call.message.answer("What is the level of education? (Higher/School):")
    await ClassifyState.human_education.set()


@dp.callback_query_handler(lambda call: call.data == "reenter", state=ClassifyState.human_nationality)
async def process_nationality_reenter(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to reenter the nationality if they click the Reenter button.
    """
    await call.message.edit_text("Please provide the nationality again:")
    await call.answer()









@dp.message_handler(state=ClassifyState.human_education)
async def process_human_education(message: types.Message, state: FSMContext):
    """
    Process the education input.
    """
    education = message.text.strip().capitalize()

    if education not in ["Higher", "School"]:
        await message.answer("Invalid input. Please enter 'Higher' or 'School'.")
        return

    await state.update_data(education=education)
    await message.answer("What is the eye color?")
    await ClassifyState.human_eye_color.set()




@dp.message_handler(state=ClassifyState.human_eye_color)
async def process_human_eye_color(message: types.Message, state: FSMContext):
    """
    Process the eye color input.
    """
    input_text = message.text.strip()

    # Validate if the input is purely text
    if not input_text.isalpha():
        await message.answer("Invalid input. Please provide a valid text-only color (e.g., Red, Blue, Green).")
        return

    # Capitalize the input and search for similar colors
    color = input_text.capitalize()
    similar_colors = get_close_matches(color, colors, n=10, cutoff=0.4)

    if not similar_colors:
        await message.answer(
            "No similar colors found. Please try again with a different input."
        )
        return

    # Create an inline keyboard with a maximum of 5 buttons per row
    keyboard = InlineKeyboardMarkup(row_width=5)
    for i, name in enumerate(similar_colors):
        keyboard.insert(InlineKeyboardButton(text=f"{i + 1}", callback_data=f"color_{i}"))
    keyboard.add(InlineKeyboardButton(text="🔄 Reenter", callback_data="reenter_color"))

    # Send the message with the results and buttons
    results = "\n".join(
        [f"{i + 1}. {name}" for i, name in enumerate(similar_colors)]
    )
    await message.answer(
        f"Did you mean one of these colors?\n\n{results}\n\n"
        "Please select one using the buttons below:",
        reply_markup=keyboard
    )

    # Store the similar colors in FSMContext
    await state.update_data(similar_colors=similar_colors)

@dp.callback_query_handler(lambda call: call.data.startswith("color_"), state=ClassifyState.human_eye_color)
async def process_color_selection(call: CallbackQuery, state: FSMContext):
    """
    Process the user's selection of color from the inline buttons.
    """
    data = await state.get_data()
    similar_colors = data.get("similar_colors")

    # Extract the selected index from the callback data
    selected_index = int(call.data.split("_")[1])
    selected_color = similar_colors[selected_index]

    # Update the state with the selected color
    await state.update_data(eye_color=selected_color)

    # Acknowledge the selection and move to the next step
    await call.message.edit_text(f"Eye color selected: {selected_color}")
    await call.answer()
    await call.message.answer("What is the hair color?")
    await ClassifyState.human_hair_color.set()


@dp.callback_query_handler(lambda call: call.data == "reenter_color", state=ClassifyState.human_eye_color)
async def process_color_reenter(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to reenter the color if they click the Reenter button.
    """
    await call.message.edit_text("Please provide the eye color again:")
    await call.answer()




@dp.message_handler(state=ClassifyState.human_hair_color)
async def process_human_hair_color(message: types.Message, state: FSMContext):
    """
    Process the hair color input.
    """
    hair_color = message.text.strip().capitalize()
    await state.update_data(hair_color=hair_color)
    await message.answer("Finally, what is the height (numeric, in cm)?")
    await ClassifyState.human_height.set()


@dp.message_handler(state=ClassifyState.human_height)
async def process_human_height(message: types.Message, state: FSMContext):
    """
    Process the height input and end the Human flow.
    """
    try:
        height = int(message.text.strip())
        if height <= 0:
            raise ValueError

        await state.update_data(height=height)
        user_data = await state.get_data()

        # Respond with the collected data
        await message.answer(
            f"Classification completed:\n"
            f"👤 Human:\n"
            f"- Gender: {user_data['gender']}\n"
            f"- Age: {user_data['age']}\n"
            f"- Nationality: {user_data['nationality']}\n"
            f"- Education: {user_data['education']}\n"
            f"- Eye Color: {user_data['eye_color']}\n"
            f"- Hair Color: {user_data['hair_color']}\n"
            f"- Height: {user_data['height']} cm"
        )

        # Finish the state
        await state.finish()

    except ValueError:
        await message.answer("Invalid input. Height must be a positive number.")
