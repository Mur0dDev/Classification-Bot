from aiogram.dispatcher.filters.state import State, StatesGroup


class ClassifyState(StatesGroup):
    """
    States for the classification process.
    """
    choose_type = State()  # User chooses a being type (Human, Animal, Alien)

    # Human-specific states
    human_gender = State()  # Asking for gender
    human_age = State()  # Asking for age
    human_nationality = State()  # Asking for nationality
    human_education = State()  # Asking for education
    human_eye_color = State()  # Asking for eye color
    human_hair_color = State()  # Asking for hair color
    human_height = State()  # Asking for height
