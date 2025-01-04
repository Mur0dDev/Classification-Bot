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
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(text="👨 Male", callback_data="gender_male"),
            InlineKeyboardButton(text="👩 Female", callback_data="gender_female"),
        )

        await call.message.answer("You selected: 👤 Human. Please provide the gender (Male/Female):", reply_markup=keyboard)
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
    await message.delete()
    await message.answer(f"✨ You have to provide your gender. Please choose one of them above: 👆🏻\n"
                         f"👨 Male or 👩 Female")


@dp.callback_query_handler(lambda call: call.data.startswith("gender_"), state=ClassifyState.human_gender)
async def process_gender_selection(call: CallbackQuery, state: FSMContext):
    """
    Process the user's gender selection.
    """
    gender = call.data.split("_")[1]  # Extract gender (male or female)

    # Save the gender to state
    await state.update_data(gender=gender.capitalize())

    # Acknowledge and move to the next step
    await call.message.edit_text(f"Gender selected: {gender.capitalize()}")
    await call.answer()
    await call.message.answer("What is your age (in years)?")
    await ClassifyState.human_age.set()


@dp.message_handler(state=ClassifyState.human_age)
async def process_human_age(message: types.Message, state: FSMContext):
    """
    Process the age input with logical limits.
    """
    try:
        age = int(message.text.strip())

        # Validate age
        if age <= 8 or age >= 101:
            await message.answer("Invalid age. Please enter a realistic age between 8 and 101.")
            return

        # Save age to state
        await state.update_data(age=age)
        await message.answer("What is your nationality?")
        await ClassifyState.human_nationality.set()
    except ValueError:
        await message.answer("Invalid input. Please enter a numeric value for age.")


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
    await ClassifyState.HUMAN_NATIONALITY.set()

    # Store the similar nationalities in FSMContext
    await state.update_data(similar_nationalities=similar_nationalities)


@dp.message_handler(state=ClassifyState.HUMAN_NATIONALITY)
async def process_human_nationality(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(f"✨ You have to choose and click from the 🔢 number(s) above\nor you have to click 🔄 Reenter to edit your entry 📝")


@dp.callback_query_handler(lambda call: call.data.startswith("nationality_"), state=ClassifyState.HUMAN_NATIONALITY)
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
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="🎓 Higher", callback_data="education_higher"),
        InlineKeyboardButton(text="🏫 School", callback_data="education_school"),
    )
    await call.message.answer("What is your level of education?", reply_markup=keyboard)
    await ClassifyState.human_education.set()


@dp.callback_query_handler(lambda call: call.data == "reenter", state=ClassifyState.HUMAN_NATIONALITY)
async def process_nationality_reenter(call: CallbackQuery, state: FSMContext):
    await ClassifyState.human_nationality.set()
    """
    Allow the user to reenter the nationality if they click the Reenter button.
    """
    await call.message.edit_text("Please provide the nationality again:")
    await call.answer()

@dp.message_handler(state=ClassifyState.human_education)
async def process_human_gender(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(f"✨ You have to provide your eduction level. Please choose one of them above: 👆🏻\n"
                         f"🎓 Higher or 🏫 School")


@dp.callback_query_handler(lambda call: call.data.startswith("education_"), state=ClassifyState.human_education)
async def process_education_selection(call: CallbackQuery, state: FSMContext):
    """
    Process the user's education level selection.
    """
    education = call.data.split("_")[1]  # Extract education level (higher or school)

    # Save the education level to state
    await state.update_data(education=education.capitalize())

    # Acknowledge and move to the next step
    await call.message.edit_text(f"Education level selected: {education.capitalize()}")
    await call.answer()
    await call.message.answer("What is your eye color?")
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
    await ClassifyState.HUMAN_EYE_COLOR.set()

    # Store the similar colors in FSMContext
    await state.update_data(similar_colors=similar_colors)

@dp.message_handler(state=ClassifyState.HUMAN_EYE_COLOR)
async def process_human_gender(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(f"✨ You have to choose and click from the 🔢 number(s) above\nor you have to click 🔄 Reenter to edit your entry 📝")


@dp.callback_query_handler(lambda call: call.data.startswith("color_"), state=ClassifyState.HUMAN_EYE_COLOR)
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


@dp.callback_query_handler(lambda call: call.data == "reenter_color", state=ClassifyState.HUMAN_EYE_COLOR)
async def process_color_reenter(call: CallbackQuery, state: FSMContext):
    await ClassifyState.human_eye_color.set()
    """
    Allow the user to reenter the color if they click the Reenter button.
    """
    await call.message.edit_text("Please provide the eye color again:")
    await call.answer()


@dp.message_handler(state=ClassifyState.human_hair_color)
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
    hair_color = input_text.capitalize()
    similar_hair_colors = get_close_matches(hair_color, colors, n=10, cutoff=0.4)

    if not similar_hair_colors:
        await message.answer(
            "No similar colors found. Please try again with a different input."
        )
        return

    # Create an inline keyboard with a maximum of 5 buttons per row
    keyboard1 = InlineKeyboardMarkup(row_width=5)
    for i, name in enumerate(similar_hair_colors):
        keyboard1.insert(InlineKeyboardButton(text=f"{i + 1}", callback_data=f"color_{i}"))
    keyboard1.add(InlineKeyboardButton(text="🔄 Reenter", callback_data="reenter_color"))

    # Send the message with the results and buttons
    results = "\n".join(
        [f"{i + 1}. {name}" for i, name in enumerate(similar_hair_colors)]
    )
    await message.answer(
        f"Did you mean one of these colors?\n\n{results}\n\n"
        "Please select one using the buttons below:",
        reply_markup=keyboard1
    )
    await ClassifyState.HUMAN_HAIR_COLOR.set()

    # Store the similar colors in FSMContext
    await state.update_data(similar_hair_colors=similar_hair_colors)


@dp.message_handler(state=ClassifyState.HUMAN_HAIR_COLOR)
async def process_human_gender(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(f"✨ You have to choose and click from the 🔢 number(s) above\nor you have to click 🔄 Reenter to edit your entry 📝")


@dp.callback_query_handler(lambda call: call.data.startswith("color_"), state=ClassifyState.HUMAN_HAIR_COLOR)
async def process_color_selection(call: CallbackQuery, state: FSMContext):
    """
    Process the user's selection of color from the inline buttons.
    """
    data = await state.get_data()
    similar_hair_colors = data.get("similar_hair_colors")

    # Extract the selected index from the callback data
    selected_index = int(call.data.split("_")[1])
    selected_color = similar_hair_colors[selected_index]

    # Update the state with the selected color
    await state.update_data(hair_color=selected_color)

    # Acknowledge the selection and move to the next step
    await call.message.edit_text(f"Hair color selected: {selected_color}")
    await call.answer()
    await call.message.answer("Finally, what is the height (numeric, in cm)?")
    await ClassifyState.human_height.set()


@dp.callback_query_handler(lambda call: call.data == "reenter_color", state=ClassifyState.HUMAN_HAIR_COLOR)
async def process_color_reenter(call: CallbackQuery, state: FSMContext):
    await ClassifyState.human_hair_color.set()
    """
    Allow the user to reenter the color if they click the Reenter button.
    """
    await call.message.edit_text("Please provide the hair color again:")
    await call.answer()


@dp.message_handler(state=ClassifyState.human_height)
async def process_human_height(message: types.Message, state: FSMContext):
    """
    Process the height input and display final data with edit/submit options.
    """
    try:
        height = int(message.text.strip())

        # Validate height
        if height < 50 or height > 250:
            await message.answer("Invalid height. Please enter a realistic height between 50 cm and 250 cm.")
            return

        # Save height to state
        await state.update_data(height=height)

        # Retrieve all gathered data
        data = await state.get_data()
        gender = data.get("gender", "Not provided")
        age = data.get("age", "Not provided")
        nationality = data.get("nationality", "Not provided")
        education = data.get("education", "Not provided")
        eye_color = data.get("eye_color", "Not provided")
        hair_color = data.get("hair_color", "Not provided")
        height = data.get("height", "Not provided")

        # Format the gathered data
        summary = (
            f"📋 **Here is the data you provided:**\n\n"
            f"👤 Gender: {gender}\n"
            f"📅 Age: {age} years\n"
            f"🌍 Nationality: {nationality}\n"
            f"🎓 Education: {education}\n"
            f"👁️ Eye Color: {eye_color}\n"
            f"💇 Hair Color: {hair_color}\n"
            f"📏 Height: {height} cm\n\n"
            "Please choose what to do next:"
        )

        # Create inline buttons
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(text="✏️ Edit Data", callback_data="edit_data"),
            InlineKeyboardButton(text="✅ Submit Data", callback_data="submit_data"),
        )

        # Send the summary and buttons
        await message.answer(summary, reply_markup=keyboard, parse_mode="Markdown")
    except ValueError:
        await message.answer("Invalid input. Please enter a numeric value for height (in cm).")


@dp.callback_query_handler(lambda call: call.data == "edit_data", state=ClassifyState.human_height)
async def handle_edit_data(call: CallbackQuery, state: FSMContext):
    """
    Display a list of steps (fields) the user can edit.
    """
    # Define editable steps
    steps = [
        ("👤 Gender", "edit_gender"),
        ("📅 Age", "edit_age"),
        ("🌍 Nationality", "edit_nationality"),
        ("🎓 Education", "edit_education"),
        ("👁️ Eye Color", "edit_eye_color"),
        ("💇 Hair Color", "edit_hair_color"),
        ("📏 Height", "edit_height"),
    ]

    # Create an inline keyboard
    keyboard = InlineKeyboardMarkup(row_width=1)
    for label, callback_data in steps:
        keyboard.add(InlineKeyboardButton(text=label, callback_data=callback_data))

    # Send the list of steps to the user
    await call.message.answer(
        "✏️ Please choose which field you'd like to edit:",
        reply_markup=keyboard,
    )
    await call.answer()

@dp.callback_query_handler(lambda call: call.data == "edit_gender", state="*")
async def edit_gender(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit their gender.
    """
    # Prompt the user to select gender again
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="👨 Male", callback_data="gender_male"),
        InlineKeyboardButton(text="👩 Female", callback_data="gender_female"),
    )
    await call.message.edit_text("👤 Please select your gender:", reply_markup=keyboard)
    await call.answer()
    await ClassifyState.human_gender.set()


@dp.callback_query_handler(lambda call: call.data == "edit_age", state="*")
async def edit_age(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit their age.
    """
    await call.message.edit_text("📅 Please provide your age (in years):")
    await call.answer()
    await ClassifyState.human_age.set()

@dp.callback_query_handler(lambda call: call.data == "edit_nationality", state="*")
async def edit_nationality(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit their nationality.
    """
    await call.message.edit_text("🌍 Please provide your nationality:")
    await call.answer()
    await ClassifyState.human_nationality.set()


@dp.callback_query_handler(lambda call: call.data == "edit_education", state="*")
async def edit_education(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit their education level.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="🎓 Higher", callback_data="education_higher"),
        InlineKeyboardButton(text="🏫 School", callback_data="education_school"),
    )
    await call.message.edit_text("🎓 Please select your education level:", reply_markup=keyboard)
    await call.answer()
    await ClassifyState.human_education.set()

@dp.callback_query_handler(lambda call: call.data == "edit_eye_color", state="*")
async def edit_eye_color(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit their eye color.
    """
    await call.message.edit_text("👁️ Please provide your eye color:")
    await call.answer()
    await ClassifyState.human_eye_color.set()


@dp.callback_query_handler(lambda call: call.data == "edit_hair_color", state="*")
async def edit_hair_color(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit their hair color.
    """
    await call.message.edit_text("💇 Please provide your hair color:")
    await call.answer()
    await ClassifyState.human_hair_color.set()



@dp.callback_query_handler(lambda call: call.data == "edit_height", state="*")
async def edit_height(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit their height.
    """
    await call.message.edit_text("📏 Please provide your height (in cm):")
    await call.answer()
    await ClassifyState.human_height.set()



