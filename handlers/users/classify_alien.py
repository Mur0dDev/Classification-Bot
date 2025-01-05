import asyncio
from datetime import datetime
from mailbox import Message
from os.path import defpath

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from loader import dp, bot
from states.classify_state import ClassifyAlienState
from data.predefined_lists import colors  # Assuming skin colors might be predefined
from utils.db_api.google_sheets import GoogleSheetsClient


# Entry point for alien classification
@dp.message_handler(state=ClassifyAlienState.humanoid)
async def start_alien_classification(message: types.Message):
    await message.delete()
    await message.answer(f"You have to choose (yes or no) from buttons above👆🏻")

# Handle humanoid selection
@dp.callback_query_handler(lambda call: call.data in ["humanoid_yes", "humanoid_no"], state=ClassifyAlienState.humanoid)
async def process_humanoid(call: CallbackQuery, state: FSMContext):
    """
    Process humanoid input.
    """
    is_humanoid = call.data == "humanoid_yes"
    await state.update_data(humanoid="Yes" if is_humanoid else "No")

    if is_humanoid:
        # If humanoid, ask for race
        await call.message.edit_text("🛸 What is the race of the alien? (e.g., X, Y, Z):")
        await ClassifyAlienState.race.set()
    else:
        """
            Handle the case where the alien is not humanoid.
            """
        # Update state with default values for the rest of the fields
        await state.update_data(
            humanoid="No",
            race="None",
            skin_color="None",
            dangerous="None",
            has_reason="None",
            weight="None"
        )

        # Fetch all collected data
        data = await state.get_data()

        # Prepare the summary of the collected data
        summary = (
            f"📋 *Alien Classification Summary*\n\n"
            f"🛸 *Humanoid*: {data.get('humanoid', 'N/A')}\n"
            f"👽 *Race*: {data.get('race', 'None')}\n"
            f"🎨 *Skin Color*: {data.get('skin_color', 'None')}\n"
            f"⚠️ *Dangerous*: {data.get('dangerous', 'None')}\n"
            f"🧐 *Has Reason*: {data.get('has_reason', 'None')}\n"
            f"⚖️ *Weight*: {data.get('weight', 'None')}\n"
        )

        # Create inline keyboard with Edit and Submit buttons
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(text="✏️ Edit Data", callback_data="edit_alien_data_no"),
            InlineKeyboardButton(text="✅ Submit Data", callback_data="submit_alien_data_no")
        )

        # Send the summary to the user
        await call.message.edit_text(summary, parse_mode="Markdown", reply_markup=keyboard)
        await call.answer()

        await state.finish()


@dp.callback_query_handler(lambda call: call.data == "edit_alien_data_no", state="*")
async def edit_humanoid_only(call: CallbackQuery, state: FSMContext):
    """
    Handle the edit process for the Humanoid question when the answer is 'No'.
    """
    # Fetch the current data
    data = await state.get_data()

    # Check if Humanoid is "No" and only allow editing that field
    if data.get("humanoid") == "No":
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(text="✅ Yes", callback_data="humanoid_yes"),
            InlineKeyboardButton(text="❌ No", callback_data="humanoid_no")
        )
        await call.message.edit_text("🛸 Is the alien humanoid? Please select one:", reply_markup=keyboard)
        await ClassifyAlienState.humanoid.set()
    else:
        # If humanoid is not "No", allow editing all fields as usual
        edit_message = (
            f"✏️ *Which field would you like to edit?*\n\n"
            f"1️⃣ Humanoid: {data.get('humanoid', 'N/A')}\n"

        )

        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(text="1️⃣ Humanoid", callback_data="edit_humanoid"),
            InlineKeyboardButton(text="✅ Done Editing", callback_data="done_editing")
        )
        await call.message.edit_text(edit_message, parse_mode="Markdown", reply_markup=keyboard)

    await call.answer()

@dp.callback_query_handler(lambda call: call.data == "submit_alien_data_no", state="*")
async def submit_alien_data_no(call: CallbackQuery, state: FSMContext):
    """
    Handle the submission of alien classification data when Humanoid is 'No'.
    Post the data to the group and save it to Google Sheets.
    """
    # Start with a "processing" message
    loading_message = await call.message.edit_text("⏳ Processing your data: 0%")

    # Incrementally update the percentage
    for i in range(10, 101, 10):  # Increment by 10% up to 100%
        await asyncio.sleep(0.5)  # Simulate processing time
        await loading_message.edit_text(f"⏳ Processing your data: {i}%")

    # Generate unique ID and current date
    unique_id = str(int(datetime.now().timestamp()))
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Initialize Google Sheets client
    sheets_client = GoogleSheetsClient(credentials_file="credentials.json",
                                       spreadsheet_name="Being Classification Data")
    sheets_client.authenticate()
    rows = sheets_client.get_data("Aliens")  # Replace "Humans" with the correct worksheet name
    row_count = len(rows)

    # Fetch all collected data
    data = await state.get_data()

    # Prepare the group message
    group_message = (
        f"📋 *Alien Classification Report*\n\n"
        f"🛸 *Humanoid*: {data.get('humanoid', 'No')}\n"
        f"👽 *Race*: {data.get('race', 'None')}\n"
        f"🎨 *Skin Color*: {data.get('skin_color', 'None')}\n"
        f"⚠️ *Dangerous*: {data.get('dangerous', 'None')}\n"
        f"🧐 *Has Reason*: {data.get('has_reason', 'None')}\n"
        f"⚖️ *Weight*: {data.get('weight', 'None')}\n"
    )

    group_id = -1002292534432  # Replace with your group ID

    try:
        # Post to Telegram group
        await bot.send_message(chat_id=group_id, text=group_message, parse_mode="Markdown")
    except Exception as e:
        await call.message.edit_text(f"❌ Failed to post to the group: {e}")
        await call.answer()
        return

    # Prepare data for Google Sheets
    row_data = [
        row_count,  # No. of line
        unique_id,   # Unique Bot Data #
        call.from_user.full_name,       # Initiator Name
        data.get("humanoid", "No"),     # Humanoid
        "None",                         # Race
        "None",                         # Skin Color
        "None",                         # Dangerous
        "None",                         # Has Reason
        "None",                         # Weight
        current_date,        # Date
    ]

    try:
        # Save to Google Sheets
        sheets_client.append_data("Aliens", row_data)  # Append to the "Aliens" worksheet

        # Acknowledge submission
        await loading_message.edit_text(
            "✅ Your data has been successfully posted to the group and saved to Google Sheets. Thank you! 🎉")
        await call.answer()

    except Exception as e:
        # Handle errors
        await call.message.edit_text(f"❌ Failed to save to Google Sheets: {e}")
        await call.answer()

    # Finish the state
    await state.finish()



@dp.message_handler(state=ClassifyAlienState.race)
async def process_alien_race(message: types.Message, state: FSMContext):
    """
    Process the alien's race input.
    """
    race = message.text.strip()
    race = race.upper()
    if race not in ["X", "Y", "Z"]:  # Validate race
        await message.answer("❌ Invalid race. Please enter X, Y, or Z.")
        return

    await state.update_data(race=race)
    await message.answer("🎨 What is the alien's skin color?")
    await ClassifyAlienState.skin_color.set()

@dp.message_handler(state=ClassifyAlienState.skin_color)
async def process_alien_skin_color(message: types.Message, state: FSMContext):
    """
    Process the alien's skin color input.
    """
    skin_color = message.text.strip().capitalize()
    if skin_color not in colors:  # Check if the color exists in predefined colors
        await message.answer(f"❌ Invalid color. Please provide a valid skin color.")
        return

    await state.update_data(skin_color=skin_color)

    # Ask if the alien is dangerous
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="✅ Yes", callback_data="dangerous_yes"),
        InlineKeyboardButton(text="❌ No", callback_data="dangerous_no"),
    )
    await message.answer("🛸 Is the alien dangerous?", reply_markup=keyboard)
    await ClassifyAlienState.dangerous.set()

@dp.message_handler(state=ClassifyAlienState.dangerous)
async def error_dangerous(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(f"You have choose yes or no button above👆🏻")

@dp.callback_query_handler(lambda call: call.data in ["dangerous_yes", "dangerous_no"], state=ClassifyAlienState.dangerous)
async def process_alien_dangerous(call: CallbackQuery, state: FSMContext):
    """
    Process if the alien is dangerous.
    """
    is_dangerous = call.data == "dangerous_yes"
    await state.update_data(dangerous="Yes" if is_dangerous else "No")

    # Ask if the alien has a reason
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="✅ Yes", callback_data="reason_yes"),
        InlineKeyboardButton(text="❌ No", callback_data="reason_no"),
    )
    await call.message.edit_text("🛸 Does the alien have a reason?", reply_markup=keyboard)
    await ClassifyAlienState.has_reason.set()

@dp.message_handler(state=ClassifyAlienState.has_reason)
async def error_dangerous(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(f"You have choose yes or no button above👆🏻")

@dp.callback_query_handler(lambda call: call.data in ["reason_yes", "reason_no"], state=ClassifyAlienState.has_reason)
async def process_alien_reason(call: CallbackQuery, state: FSMContext):
    """
    Process if the alien has a reason.
    """
    has_reason = call.data == "reason_yes"
    await state.update_data(has_reason="Yes" if has_reason else "No")

    await call.message.edit_text("⚖️ What is the alien's weight (in kg)?")
    await ClassifyAlienState.weight.set()


@dp.message_handler(state=ClassifyAlienState.weight)
async def process_alien_weight(message: types.Message, state: FSMContext):
    """
    Process the alien's weight input and display all collected data.
    """
    weight = message.text.strip()

    # Validate weight
    if not weight.isdigit() or int(weight) <= 0:
        await message.answer("❌ Invalid weight. Please provide a valid weight in kilograms.")
        return

    # Save weight to state
    await state.update_data(weight=f"{weight} kg")

    # Fetch all collected data
    data = await state.get_data()

    # Prepare the summary of the collected data
    summary = (
        f"📋 *Alien Classification Summary*\n\n"
        f"🛸 *Humanoid*: {data.get('humanoid', 'N/A')}\n"
        f"👽 *Race*: {data.get('race', 'N/A')}\n"
        f"🎨 *Skin Color*: {data.get('skin_color', 'N/A')}\n"
        f"⚠️ *Dangerous*: {data.get('dangerous', 'N/A')}\n"
        f"🧐 *Has Reason*: {data.get('has_reason', 'N/A')}\n"
        f"⚖️ *Weight*: {data.get('weight', 'N/A')}\n"
    )

    # Display final summary with options
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="✏️ Edit Data", callback_data="edit_alien_data"),
        InlineKeyboardButton(text="✅ Submit Data", callback_data="submit_alien_data")
    )

    # Send summary to the user
    await message.answer(summary, parse_mode="Markdown", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data == "edit_alien_data", state="*")
async def edit_alien_data(call: CallbackQuery, state: FSMContext):
    """
    Handle the edit data process for alien classification.
    Allow the user to select which field to edit.
    """
    # Fetch all collected data
    data = await state.get_data()

    # Prepare a message with the current data and edit options
    edit_message = (
        f"✏️ *Which field would you like to edit?*\n\n"
        f"1️⃣ Humanoid: {data.get('humanoid', 'N/A')}\n"
        f"2️⃣ Race: {data.get('race', 'N/A')}\n"
        f"3️⃣ Skin Color: {data.get('skin_color', 'N/A')}\n"
        f"4️⃣ Dangerous: {data.get('dangerous', 'N/A')}\n"
        f"5️⃣ Has Reason: {data.get('has_reason', 'N/A')}\n"
        f"6️⃣ Weight: {data.get('weight', 'N/A')}\n"
    )

    # Create an inline keyboard with options to edit specific fields
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="1️⃣ Humanoid", callback_data="edit_humanoid"),
        InlineKeyboardButton(text="2️⃣ Race", callback_data="edit_race"),
        InlineKeyboardButton(text="3️⃣ Skin Color", callback_data="edit_skin_color"),
        InlineKeyboardButton(text="4️⃣ Dangerous", callback_data="edit_dangerous"),
        InlineKeyboardButton(text="5️⃣ Has Reason", callback_data="edit_has_reason"),
        InlineKeyboardButton(text="6️⃣ Weight", callback_data="edit_weight"),
        InlineKeyboardButton(text="✅ Done Editing", callback_data="done_editing"),
    )

    # Send the edit options to the user
    await call.message.edit_text(edit_message, parse_mode="Markdown", reply_markup=keyboard)
    await call.answer()

@dp.callback_query_handler(lambda call: call.data == "edit_humanoid", state="*")
async def edit_humanoid(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit the humanoid field.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="✅ Yes", callback_data="humanoid_yes"),
        InlineKeyboardButton(text="❌ No", callback_data="humanoid_no"),
    )
    await call.message.edit_text("🛸 Is the alien humanoid? Please select one:", reply_markup=keyboard)
    await ClassifyAlienState.humanoid.set()


@dp.callback_query_handler(lambda call: call.data == "edit_race", state="*")
async def edit_race(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit the race field.
    """
    await call.message.edit_text("🛸 What is the race of the alien? (e.g., X, Y, Z):")
    await ClassifyAlienState.race.set()

@dp.callback_query_handler(lambda call: call.data == "edit_skin_color", state="*")
async def edit_skin_color(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit the skin color field.
    """
    await call.message.edit_text("🎨 What is the alien's skin color?")
    await ClassifyAlienState.skin_color.set()

@dp.callback_query_handler(lambda call: call.data == "edit_dangerous", state="*")
async def edit_dangerous(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit the dangerous field.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="✅ Yes", callback_data="dangerous_yes"),
        InlineKeyboardButton(text="❌ No", callback_data="dangerous_no"),
    )
    await call.message.edit_text("⚠️ Is the alien dangerous?", reply_markup=keyboard)
    await ClassifyAlienState.dangerous.set()

@dp.callback_query_handler(lambda call: call.data == "edit_has_reason", state="*")
async def edit_has_reason(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit the has_reason field.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="✅ Yes", callback_data="reason_yes"),
        InlineKeyboardButton(text="❌ No", callback_data="reason_no"),
    )
    await call.message.edit_text("🧐 Does the alien have a reason?", reply_markup=keyboard)
    await ClassifyAlienState.has_reason.set()

@dp.callback_query_handler(lambda call: call.data == "edit_weight", state="*")
async def edit_weight(call: CallbackQuery, state: FSMContext):
    """
    Allow the user to edit the weight field.
    """
    await call.message.edit_text("⚖️ What is the alien's weight (in kg)?")
    await ClassifyAlienState.weight.set()

@dp.callback_query_handler(lambda call: call.data == "done_editing", state="*")
async def done_editing(call: CallbackQuery, state: FSMContext):
    """
    Finish editing and return to the final data display.
    """
    data = await state.get_data()

    # Prepare the summary of the collected data
    summary = (
        f"📋 *Alien Classification Summary*\n\n"
        f"🛸 *Humanoid*: {data.get('humanoid', 'N/A')}\n"
        f"👽 *Race*: {data.get('race', 'N/A')}\n"
        f"🎨 *Skin Color*: {data.get('skin_color', 'N/A')}\n"
        f"⚠️ *Dangerous*: {data.get('dangerous', 'N/A')}\n"
        f"🧐 *Has Reason*: {data.get('has_reason', 'N/A')}\n"
        f"⚖️ *Weight*: {data.get('weight', 'N/A')}\n"
    )

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="✏️ Edit Data", callback_data="edit_alien_data"),
        InlineKeyboardButton(text="✅ Submit Data", callback_data="submit_alien_data")
    )

    await call.message.edit_text(summary, parse_mode="Markdown", reply_markup=keyboard)
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == "submit_alien_data", state="*")
async def submit_alien_data(call: CallbackQuery, state: FSMContext):
    """
    Handle the submission of alien classification data.
    Post the data to the group and save it to Google Sheets.
    """
    # Start with a "processing" message
    loading_message = await call.message.edit_text("⏳ Processing your data: 0%")

    # Incrementally update the percentage
    for i in range(10, 101, 10):  # Increment by 10% up to 100%
        await asyncio.sleep(0.5)  # Simulate processing time
        await loading_message.edit_text(f"⏳ Processing your data: {i}%")

    # Generate unique ID and current date
    unique_id = str(int(datetime.now().timestamp()))
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Initialize Google Sheets client
    sheets_client = GoogleSheetsClient(credentials_file="credentials.json",
                                       spreadsheet_name="Being Classification Data")
    sheets_client.authenticate()
    rows = sheets_client.get_data("Aliens")  # Replace "Humans" with the correct worksheet name
    row_count = len(rows)
    # Fetch all collected data
    data = await state.get_data()

    # Prepare the group message
    group_message = (
        f"📋 *Alien Classification Report*\n\n"
        f"🛸 *Humanoid*: {data.get('humanoid', 'N/A')}\n"
        f"👽 *Race*: {data.get('race', 'N/A')}\n"
        f"🎨 *Skin Color*: {data.get('skin_color', 'N/A')}\n"
        f"⚠️ *Dangerous*: {data.get('dangerous', 'N/A')}\n"
        f"🧐 *Has Reason*: {data.get('has_reason', 'N/A')}\n"
        f"⚖️ *Weight*: {data.get('weight', 'N/A')}\n"
    )

    group_id = -1002292534432  # Replace with your group ID

    try:
        # Post to Telegram group
        await bot.send_message(chat_id=group_id, text=group_message, parse_mode="Markdown")
    except Exception as e:
        await call.message.edit_text(f"❌ Failed to post to the group: {e}")
        await call.answer()
        return

    # Prepare data for Google Sheets
    row_data = [
        row_count,  # No. of line (to be dynamically calculated)
        unique_id,   # Unique Bot Data #
        call.from_user.full_name,       # Initiator Name
        data.get("humanoid", "N/A"),    # Humanoid
        data.get("race", "N/A"),        # Race
        data.get("skin_color", "N/A"),  # Skin Color
        data.get("dangerous", "N/A"),   # Dangerous
        data.get("has_reason", "N/A"),  # Has Reason
        data.get("weight", "N/A"),      # Weight
        current_date,        # Date
    ]

    try:
        # Save to Google Sheets
        sheets_client.append_data("Aliens", row_data)  # Append to the "Aliens" worksheet

        # Acknowledge submission
        await loading_message.edit_text(
            "✅ Your data has been successfully posted to the group and saved to Google Sheets. Thank you! 🎉")
        await call.answer()

    except Exception as e:
        # Handle errors
        await call.message.edit_text(f"❌ Failed to save to Google Sheets: {e}")
        await call.answer()

    # Finish the state
    await state.finish()
