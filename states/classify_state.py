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
    SPECIES = State()
    mammal = State()  # Collect mammal (Yes/No)
    predator = State()  # Collect predator (Yes/No)
    color = State()  # Collect color
    weight = State()  # Collect weight
    age = State()  # Collect age


class ClassifyAlienState(StatesGroup):
    humanoid = State()  # Step to determine if the alien is humanoid
    race = State()      # Step to input the alien's race
    skin_color = State()  # Step to input the skin color
    dangerous = State()   # Step to determine if the alien is dangerous
    has_reason = State()  # Step to determine if the alien has a reason
    weight = State()      # Step to input the alien's weight

