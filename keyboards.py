from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def generate_start_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn = KeyboardButton(text='Начать регистрацию')
    markup.add(btn)
    return markup

def generate_genders_buttons():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    male = KeyboardButton(text='Мужской')
    female = KeyboardButton(text='Женский')
    markup.row(male, female) # Заливаю в один ряд = [ Мужской ][ Женский ]
    return markup

