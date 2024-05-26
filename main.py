# Виртуальное окружение, библиотека "aiogram" версии 2.24.
# aiogram - асинхронная библиотека. Функции в ней нужно писать асинхронно.
# Функции будут в какой-то момент времени будут приостанавливаться для
# выполнения другой функции у другого пользователя
# pip install aiogram==2.24

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, ReplyKeyboardRemove
from database import DataBase
from keyboards import generate_start_button, generate_genders_buttons
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from states import Register


# https://t.me/tirlikurenduy_bot
bot = Bot(token='')
storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)
db = DataBase()

@dp.message_handler(commands=['start'])
async def command_start(message: Message):
    chat_id = message.chat.id
    db.create_users_table()
    user = db.get_user_by_chat_id(chat_id)
    if user: # Если что-то есть
        # (1, 3407893, None, None, None, None, None)
        if user[2] is None or user[3] is None or user[4] is None or user[5] is None or user[6] is None or user[2] is None:
            await bot.send_message(chat_id, 'У вас не заполнены некоторые данные. Попробуйте снова',
                                   reply_markup=generate_start_button())
        else:
            await bot.send_message(chat_id, 'Вы уже прошли опрос. Данные сохранены.')
    else:
        db.first_register_user(chat_id) # Автоматом регистрируем пользователя
        await bot.send_message(chat_id, 'Чтобы пройти регистрацию, нажмите на кнопку ниже',
                               reply_markup=generate_start_button())



@dp.message_handler(regexp='Начать регистрацию')
async def start_register(message: Message):
    chat_id = message.chat.id
    await Register.full_name.set() # Сейчас будет вопрос
    await bot.send_message(chat_id, 'Введите ваши фамилию и имя')

@dp.message_handler(state=Register.full_name)
async def get_full_name_ask_gender(message: Message, state: FSMContext):
    chat_id = message.chat.id
    await state.update_data(full_name=message.text)
    await Register.gender.set()
    await bot.send_message(chat_id, 'Выберите свой пол: ',
                           reply_markup=generate_genders_buttons())

@dp.message_handler(regexp='(Мужской|Женский)', state=Register.gender)
async def get_gender(message: Message, state: FSMContext):
    chat_id = message.chat.id
    await state.update_data(gender=message.text)
    await Register.age.set()
    await bot.send_message(chat_id, 'Введите ваш возраст: ',
                           reply_markup=ReplyKeyboardRemove())

@dp.message_handler(regexp='\d\d', state=Register.age)
async def get_age_ask_phone(message: Message, state: FSMContext):
    chat_id = message.chat.id
    await state.update_data(age=message.text)
    await Register.phone.set()
    await bot.send_message(chat_id, 'Введите свой номер телефона в формате +998123456789: ')

@dp.message_handler(regexp='\+998\d{9}', state=Register.phone)
async def get_phone_ask_profession(message: Message, state: FSMContext):
    chat_id = message.chat.id
    await state.update_data(phone=message.text)
    await Register.profession.set()
    await bot.send_message(chat_id, 'Введите вашу должность: ')

@dp.message_handler(state=Register.profession)
async def get_profession_save_data(message: Message, state: FSMContext):
    chat_id = message.chat.id
    profession = message.text
    data = await state.get_data()
    db.update_data(chat_id, data['full_name'], data['gender'], data['age'], data['phone'], profession)
    await state.finish()
    await bot.send_message(chat_id, 'Вы успешно зарегистрировались. Будем вас ждать')
    await command_start(message)


@dp.message_handler(commands=['export'])
async def export_data(message: Message):
    chat_id = message.chat.id
    db.save_data_for_excel()
    with open('result.xlsx', mode='rb') as file:
        await bot.send_document(chat_id, file)

executor.start_polling(dp)
