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
    HUMAN_NATIONALITY = State()  # Asking for nationality
    human_education = State()  # Asking for education
    human_eye_color = State()  # Asking for eye color
    HUMAN_EYE_COLOR = State()  # Asking for eye color
    human_hair_color = State()  # Asking for hair color
    HUMAN_HAIR_COLOR = State()  # Asking for hair color
    human_height = State()  # Asking for height

class ClassifyAnimalState(StatesGroup):
    species = State()  # Collect species
    mammal = State()  # Collect mammal (Yes/No)
    predator = State()  # Collect predator (Yes/No)
    color = State()  # Collect color
    weight = State()  # Collect weight
    age = State()  # Collect age
