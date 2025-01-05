import asyncio
from datetime import datetime
from difflib import get_close_matches
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp, bot
from filters import IsPrivate
from data.predefined_lists import animals, colors
from states.classify_state import ClassifyAnimalState
from utils.db_api.google_sheets import GoogleSheetsClient

@dp.message_handler(IsPrivate(), state=ClassifyAnimalState.species)
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
    await ClassifyAnimalState.SPECIES.set()

    # Store the similar animals in FSMContext
    await state.update_data(similar_animals=similar_animals)


@dp.message_handler(IsPrivate(), state=ClassifyAnimalState.SPECIES)
async def process_animal_species_repeat(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer("✨ You have to choose and click from the 🔢 number(s) above\nor you have to click 🔄 Reenter to edit your entry 📝")


@dp.callback_query_handler(lambda call: call.data.startswith("animal_"), state=ClassifyAnimalState.SPECIES)
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
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="✅ Yes", callback_data="mammal_yes"),
        InlineKeyboardButton(text="❌ No", callback_data="mammal_no")
    )

    await call.message.answer("🦘 Is this a mammal? (Yes/No)\n\nPlease select one:", reply_markup=keyboard)
    await ClassifyAnimalState.mammal.set()


@dp.callback_query_handler(lambda call: call.data == "reenter_species", state=ClassifyAnimalState.SPECIES)
async def process_animal_reenter(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to reenter the species if they click the Reenter button.
    """
    await ClassifyAnimalState.species.set()
    await call.message.edit_text("Please provide the species again:")
    await call.answer()

@dp.message_handler(IsPrivate(), state=ClassifyAnimalState.mammal)
async def process_animal_mammal(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(f"You have to choose, yes or no button above\nnothing else is accepted")

@dp.callback_query_handler(lambda call: call.data in ["mammal_yes", "mammal_no"], state=ClassifyAnimalState.mammal)
async def process_mammal_response(call: CallbackQuery, state: FSMContext):
    """
    Process the user's selection for the mammal question.
    """
    is_mammal = call.data.split("_")[1].capitalize()  # Extract 'Yes' or 'No'
    await state.update_data(mammal=is_mammal)

    # Acknowledge the user's response and move to the next question
    await call.message.edit_text(f"🦘 Mammal: {is_mammal}")
    await call.answer()

    # Move to the next step: Is this a predator?
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="🦁 Yes", callback_data="predator_yes"),
        InlineKeyboardButton(text="🐾 No", callback_data="predator_no")
    )

    await call.message.answer("🦁 Is this a predator? Please select one:", reply_markup=keyboard)
    await ClassifyAnimalState.predator.set()

@dp.message_handler(IsPrivate(), state=ClassifyAnimalState.predator)
async def process_animal_mammal(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(f"You have to choose, yes or no button above\nnothing else is accepted")

@dp.callback_query_handler(lambda call: call.data in ["predator_yes", "predator_no"], state=ClassifyAnimalState.predator)
async def process_predator_response(call: CallbackQuery, state: FSMContext):
    """
    Process the user's response for whether the animal is a predator.
    """
    is_predator = call.data.split("_")[1].capitalize()  # Extract 'Yes' or 'No'
    await state.update_data(predator=is_predator)

    # Acknowledge the user's response
    await call.message.edit_text(f"🦁 Predator: {is_predator}")
    await call.answer()

    # Move to the next step: Animal color
    await call.message.answer("🎨 What is the color of the animal? (e.g., Brown, White, Black):")
    await ClassifyAnimalState.color.set()


@dp.message_handler(IsPrivate(), state=ClassifyAnimalState.color)
async def process_animal_color(message: types.Message, state: FSMContext):
    """
    Process the color input.
    """
    input_text = message.text.strip()

    # Validate if the input is purely text
    if not input_text.isalpha():
        await message.answer("❌ Invalid input. Please provide a valid text-only color (e.g., Brown, Black, White).")
        return

    # Capitalize the input and search for similar colors
    color_input = input_text.capitalize()
    similar_colors = get_close_matches(color_input, colors, n=10, cutoff=0.4)

    if not similar_colors:
        await message.answer("❌ No similar colors found. Please try again with a different input.")
        return

    # Create a dynamic inline keyboard for color selection
    keyboard = InlineKeyboardMarkup(row_width=5)
    for i, color in enumerate(similar_colors):
        keyboard.insert(InlineKeyboardButton(text=f"{i + 1}", callback_data=f"color_{i}"))
    keyboard.add(InlineKeyboardButton(text="🔄 Reenter", callback_data="reenter_color"))

    # Send the message with the results and buttons
    results = "\n".join([f"{i + 1}. {color}" for i, color in enumerate(similar_colors)])
    await message.answer(
        f"🎨 Did you mean one of these colors?\n\n{results}\n\n"
        "Please select one using the buttons below:",
        reply_markup=keyboard
    )

    # Save the similar colors in FSMContext for later selection
    await state.update_data(similar_colors=similar_colors)

@dp.callback_query_handler(lambda call: call.data.startswith("color_"), state=ClassifyAnimalState.color)
async def process_color_selection(call: CallbackQuery, state: FSMContext):
    """
    Process the user's selection of a color from the inline buttons.
    """
    data = await state.get_data()
    similar_colors = data.get("similar_colors")

    try:
        # Extract the selected index from the callback data
        selected_index = int(call.data.split("_")[1])
        selected_color = similar_colors[selected_index]

        # Save the selected color to the state
        await state.update_data(color=selected_color)

        # Acknowledge the selection and move to the next step
        await call.message.edit_text(f"🎨 Color selected: {selected_color}")
        await call.answer()

        # Ask the user for the animal's weight
        await call.message.answer("⚖️ What is the weight of the animal? (in kg):")
        await ClassifyAnimalState.weight.set()
    except (ValueError, IndexError):
        await call.answer("❌ An error occurred while processing your selection. Please try again.", show_alert=True)


@dp.callback_query_handler(lambda call: call.data == "reenter_color", state=ClassifyAnimalState.color)
async def process_color_reenter(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to reenter the color if they click the Reenter button.
    """
    await ClassifyAnimalState.color.set()
    await call.message.edit_text("🎨 Please provide the color again:")
    await call.answer()

@dp.message_handler(IsPrivate(), state=ClassifyAnimalState.weight)
async def process_animal_weight(message: types.Message, state: FSMContext):
    """
    Process the weight input.
    """
    input_text = message.text.strip()

    # Validate if the input is numeric
    if not input_text.isdigit():
        await message.answer("❌ Invalid input. Please provide a numeric value for the weight (e.g., 15, 200).")
        return

    # Convert input to integer and validate the range
    weight = int(input_text)
    if weight <= 0 or weight > 10000:  # Assuming 10,000 kg is a reasonable maximum weight for an animal
        await message.answer("❌ Invalid weight. Please provide a realistic weight value (e.g., between 1 and 10,000 kg).")
        return

    # Save the weight to the state
    await state.update_data(weight=weight)

    # Acknowledge the weight and move to the next step
    await message.answer(f"⚖️ Weight: {weight} kg recorded.")
    await message.answer("📅 What is the age of the animal? (in months):")
    await ClassifyAnimalState.age.set()


@dp.message_handler(IsPrivate(), state=ClassifyAnimalState.age)
async def process_animal_age(message: types.Message, state: FSMContext):
    """
    Process the age input.
    """
    input_text = message.text.strip()

    # Validate if the input is numeric
    if not input_text.isdigit():
        await message.answer("❌ Invalid input. Please provide a numeric value for the age (e.g., 12, 60).")
        return

    # Convert input to integer and validate the range
    age = int(input_text)
    if age < 0 or age > 3600:  # Assuming 3600 months (~300 years) is a reasonable maximum age for an animal
        await message.answer("❌ Invalid age. Please provide a realistic age value (e.g., between 0 and 3600 months).")
        return

    # Save the age to the state
    await state.update_data(age=age)

    # Acknowledge the age and finish the classification process
    await message.answer(f"📅 Age: {age} months recorded.")
    await message.answer("✅ Classification complete! You can now submit the data or edit it.")

    """
        Display the final collected data to the user for review.
        """
    data = await state.get_data()
    summary = (
        f"📋 Here is the data you provided:\n\n"
        f"🦘 Species: {data.get('species', 'Not provided')}\n"
        f"✅ Mammal: {data.get('mammal', 'Not provided')}\n"
        f"🦁 Predator: {data.get('predator', 'Not provided')}\n"
        f"🎨 Color: {data.get('color', 'Not provided')}\n"
        f"⚖️ Weight: {data.get('weight', 'Not provided')} kg\n"
        f"📅 Age: {data.get('age', 'Not provided')} months\n\n"
        f"You can now submit the data or edit it."
    )

    # Add buttons for editing or submitting
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="✏️ Edit Data", callback_data="edit_animal_data"),
        InlineKeyboardButton(text="✅ Submit Data", callback_data="submit_animal_data")
    )

    # Display the final summary
    await message.answer(summary, reply_markup=keyboard)
    # await message.answer()


@dp.callback_query_handler(lambda call: call.data == "edit_animal_data", state="*")
async def edit_animal_data(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit specific parts of the animal classification data.
    """
    data = await state.get_data()
    # Generate a list of editable steps
    steps = [
        f"1. Species: {data.get('species', 'Not provided')}",
        f"2. Mammal: {data.get('mammal', 'Not provided')}",
        f"3. Predator: {data.get('predator', 'Not provided')}",
        f"4. Color: {data.get('color', 'Not provided')}",
        f"5. Weight: {data.get('weight', 'Not provided')} kg",
        f"6. Age: {data.get('age', 'Not provided')} months"
    ]
    steps_text = "\n".join(steps)

    keyboard = InlineKeyboardMarkup(row_width=3)
    for i in range(1, 7):
        keyboard.insert(InlineKeyboardButton(text=f"{i}", callback_data=f"edit_animal_{i}"))
    keyboard.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_edit"))

    await call.message.edit_text(
        f"✏️ Select the part you want to edit:\n\n{steps_text}",
        reply_markup=keyboard
    )
    await call.answer()

@dp.callback_query_handler(lambda call: call.data == "edit_animal_1", state="*")
async def edit_species(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to reenter the species.
    """
    await ClassifyAnimalState.species.set()
    await call.message.edit_text("🦘 Please provide the species again:")
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == "edit_animal_2", state="*")
async def edit_mammal(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to reenter the mammal data.
    """
    await ClassifyAnimalState.mammal.set()
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="✅ Yes", callback_data="mammal_yes"),
        InlineKeyboardButton(text="❌ No", callback_data="mammal_no")
    )
    await call.message.edit_text("🦘 Is this a mammal? Please select one:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == "edit_animal_3", state="*")
async def edit_predator(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to reenter the predator data.
    """
    await ClassifyAnimalState.predator.set()
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="🦁 Yes", callback_data="predator_yes"),
        InlineKeyboardButton(text="🐾 No", callback_data="predator_no")
    )
    await call.message.edit_text("🦁 Is this a predator? Please select one:", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == "edit_animal_4", state="*")
async def edit_color(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to reenter the color data.
    """
    await ClassifyAnimalState.color.set()
    await call.message.edit_text("🎨 Please provide the color again:")
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == "edit_animal_5", state="*")
async def edit_weight(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to reenter the weight data.
    """
    await ClassifyAnimalState.weight.set()
    await call.message.edit_text("⚖️ Please provide the weight again (in kg):")
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == "edit_animal_6", state="*")
async def edit_age(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to reenter the age data.
    """
    await ClassifyAnimalState.age.set()
    await call.message.edit_text("📅 Please provide the age again (in months):")
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == "edit_animal_6", state="*")
async def edit_age(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to reenter the age data.
    """
    await ClassifyAnimalState.age.set()
    await call.message.edit_text("📅 Please provide the age again (in months):")
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == "submit_animal_data", state="*")
async def submit_animal_data(call: CallbackQuery, state: FSMContext):
    """
    Submit the final animal classification data.
    """

    # Start with a "processing" message
    loading_message = await call.message.edit_text("⏳ Processing your data: 0%")

    # Incrementally update the percentage
    for i in range(10, 101, 10):  # Increment by 10% up to 100%
        await asyncio.sleep(0.5)  # Simulate processing time
        await loading_message.edit_text(f"⏳ Processing your data: {i}%")

    data = await state.get_data()
    # Telegram group ID
    group_id = -1002292534432  # Replace with your actual group ID

    # Initialize Google Sheets client
    sheets_client = GoogleSheetsClient(credentials_file="credentials.json",
                                       spreadsheet_name="Being Classification Data")
    sheets_client.authenticate()

    # Generate unique ID and current date
    unique_id = str(int(datetime.now().timestamp()))
    current_date = datetime.now().strftime("%Y-%m-%d")
    rows = sheets_client.get_data("Animals")  # Replace "Humans" with the correct worksheet name
    row_count = len(rows)

    try:
        # Prepare data for submission
        row_data = [
            row_count,  # No. of line (You need to calculate this dynamically)
            unique_id,
            call.from_user.full_name,
            data.get("species", "N/A"),    # Species
            data.get("mammal", "N/A"),     # Mammal
            data.get("predator", "N/A"),   # Predator
            data.get("color", "N/A"),      # Color
            data.get("weight", "N/A"),     # Weight
            data.get("age", "N/A"),        # Age
            current_date       # Date
        ]

        # Format the message template for group posting
        group_message = (
            f"📋 *Animal Classification Report*\n\n"
            f"🔢 *ID*: #{unique_id}\n"
            f"📅 *Date*: {current_date}\n\n"
            f"🦘 *Species*: {data.get('species', 'N/A')}\n"
            f"✅ *Mammal*: {data.get('mammal', 'N/A')}\n"
            f"🦁 *Predator*: {data.get('predator', 'N/A')}\n"
            f"🎨 *Color*: {data.get('color', 'N/A')}\n"
            f"⚖️ *Weight*: {data.get('weight', 'N/A')} kg\n"
            f"📅 *Age*: {data.get('age', 'N/A')} months\n"
        )

        # Post to Telegram group
        await bot.send_message(chat_id=group_id, text=group_message)
        sheets_client.append_data("Animals", row_data)

        # Final success message
        await loading_message.edit_text(
            "✅ Your data has been successfully posted to the group and saved to Google Sheets. Thank you! 🎉")
        await call.answer()

    except Exception as e:
        # Handle errors
        await call.message.edit_text(f"❌ An error occurred: {e}. Please try again.")
        await call.answer()

    # Finish the state
    await state.finish()
