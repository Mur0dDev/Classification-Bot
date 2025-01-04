from aiogram.dispatcher.filters.state import State, StatesGroup

class ClassifyState(StatesGroup):
    """
    States for the classification process.
    """
    choose_type = State()  # User chooses a being type (Human, Animal, Alien)
