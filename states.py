from aiogram.dispatcher.filters.state import State, StatesGroup

class Register(StatesGroup):
    full_name = State()
    gender = State()
    age = State()
    phone = State()
    profession = State()
