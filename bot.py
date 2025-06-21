

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# Настройка логирования
logging.basicConfig(level=logging.INFO)
bot = Bot(token="6643113653:AAF0O9s6urEjo7uRF30SwNuBYBIwiI9D-0c")
dp = Dispatcher(bot)

# Словари для расчёта
base_prices = {
    "Новостройка (бетон)": 24050,
    "Новостройка (whitebox)": 5460
}

floor_prices = {
    "Ламинат": 2535,
    "Кварцвинил": 2795,
    "Инженерная доска": 4420,
    "Керамогранит": 5330
}

wall_prices = {
    "Обои": 2600,
    "Обои под покраску": 5950,
    "Стены под покраску": 10000
}

ceiling_prices = {
    "Натяжной потолок": 2100,
    "Оштукатуренный потолок под покраску": 7660,
    "Гипсокартоновый потолок под покраску": 8320
}

# Словарь для хранения данных пользователя
user_data = {}

# Обработчик для команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    # Кнопки
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("Получить консультацию", url="https://t.me/ariadnahome_pro")
    button2 = InlineKeyboardButton("Новый расчёт", callback_data="start_calculation")
    keyboard.add(button1, button2)

    await message.answer("Добро пожаловать! Вы можете начать новый расчёт или связаться с нами.",
                         reply_markup=keyboard)

# Обработчик для кнопки "Новый расчёт"
@dp.callback_query_handler(lambda c: c.data == 'start_calculation')
async def new_calculation_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Введите площадь квартиры (м²):")

# Обработчик для ввода площади
@dp.message_handler(lambda message: message.text.isdigit())
async def process_area(message: types.Message):
    user_data[message.from_user.id] = {"area": int(message.text)}
    await message.answer("Выберите тип квартиры:", reply_markup=types.ReplyKeyboardMarkup([
        ["Новостройка (бетон)", "Новостройка (whitebox)"]
    ]))

# Обработчик для типа квартиры
@dp.message_handler(lambda message: message.text in ["Новостройка (бетон)", "Новостройка (whitebox)"])
async def process_base(message: types.Message):
    user_data[message.from_user.id]["base"] = message.text
    await message.answer("Выберите тип пола:", reply_markup=types.ReplyKeyboardMarkup([
        ["Ламинат", "Кварцвинил", "Инженерная доска", "Керамогранит"]
    ]))

# Обработчик для типа пола
@dp.message_handler(lambda message: message.text in ["Ламинат", "Кварцвинил", "Инженерная доска", "Керамогранит"])
async def process_floor(message: types.Message):
    user_data[message.from_user.id]["floor"] = message.text
    await message.answer("Выберите тип отделки стен:", reply_markup=types.ReplyKeyboardMarkup([
        ["Обои", "Обои под покраску", "Стены под покраску"]
    ]))

# Обработчик для типа отделки стен
@dp.message_handler(lambda message: message.text in ["Обои", "Обои под покраску", "Стены под покраску"])
async def process_walls(message: types.Message):
    user_data[message.from_user.id]["walls"] = message.text
    await message.answer("Выберите тип потолка:", reply_markup=types.ReplyKeyboardMarkup([
        ["Натяжной потолок", "Оштукатуренный потолок под покраску", "Гипсокартоновый потолок под покраску"]
    ]))

# Обработчик для типа потолка
@dp.message_handler(lambda message: message.text in ["Натяжной потолок", "Оштукатуренный потолок под покраску", "Гипсокартоновый потолок под покраску"])
async def process_ceiling(message: types.Message):
    user_data[message.from_user.id]["ceiling"] = message.text

    # Выполняем расчёт
    base = user_data[message.from_user.id]["base"]
    floor = user_data[message.from_user.id]["floor"]
    walls = user_data[message.from_user.id]["walls"]
    ceiling = user_data[message.from_user.id]["ceiling"]
    area = user_data[message.from_user.id]["area"]

    total_cost = (base_prices[base] + floor_prices[floor] + wall_prices[walls] + ceiling_prices[ceiling]) * area


# Отправляем результат в группу
    group_id = "-1002528008430"  # ID группы
    await bot.send_message(group_id, 
        f"Новый расчёт для {message.from_user.full_name} (ID: {message.from_user.id})\n"
        f"Тип квартиры: {base}\n"
        f"Тип пола: {floor}\n"
        f"Тип отделки стен: {walls}\n"
        f"Тип потолка: {ceiling}\n"
        f"Площадь квартиры: {area} м²\n"
        f"Стоимость: {total_cost} рублей"
    )

    # Отправляем результат пользователю
    await message.answer(
        f"Тип квартиры: {base}\n"
        f"Тип пола: {floor}\n"
        f"Тип отделки стен: {walls}\n"
        f"Тип потолка: {ceiling}\n"
        f"Площадь квартиры: {area} м²\n"
        f"Стоимость: {total_cost} рублей",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Получить консультацию", url="https://t.me/ariadnahome_pro"),
            InlineKeyboardButton("Новый расчёт", callback_data="start_calculation")
        )
    )

# Обработчик для групповых сообщений
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_group_message(message: types.Message):
    if message.chat.type == 'supergroup':
        if "сколько стоит" in message.text.lower():
            await message.answer("Вы можете рассчитать стоимость ремонта с помощью нашего бота, отправив команду /start.")
        elif "расчёт ремонта" in message.text.lower():
            await message.answer("Напишите команду /start, чтобы начать расчёт стоимости ремонта.")
        else:
            await message.answer("Если у вас есть вопросы по стоимости ремонта, напишите команду /start для расчёта.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)