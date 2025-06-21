
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

# Словари для цен на дизайн
design_prices = {
    "Обмерный план": 750,
    "3D коллажи": 1000,
    "Чертежи": 750,
    "Планировочное решение": 750,
    "3D визуализация": 1500
}

# Обработчик для команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    # Кнопки
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("Написать в личный Telegram", url="https://t.me/ariadnahome_pro")
    button2 = InlineKeyboardButton("Новый расчёт", callback_data="start_calculation")
    button3 = InlineKeyboardButton("Дизайн интерьера", callback_data="design_calculation")
    keyboard.add(button1, button2, button3)

    await message.answer("Добро пожаловать! Вы можете начать новый расчёт или связаться с нами.",
                         reply_markup=keyboard)

# Обработчик для кнопки "Новый расчёт" - Начало расчета ремонта
@dp.callback_query_handler(lambda c: c.data == 'start_calculation')
async def new_calculation_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Введите площадь квартиры для ремонта (м²):")

# Обработчик для кнопки "Дизайн интерьера"
@dp.callback_query_handler(lambda c: c.data == 'design_calculation')
async def design_calculation_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Введите площадь квартиры для дизайна (м²):")

# Обработчик для ввода площади при расчете дизайна
@dp.message_handler(lambda message: message.text.isdigit(), state="*")
async def process_area(message: types.Message):
    if message.text.isdigit():
        user_data[message.from_user.id] = {"area": int(message.text)}
        await message.answer("Выберите тип квартиры для дизайна:", reply_markup=types.ReplyKeyboardMarkup([
            ["Новостройка (бетон)", "Новостройка (whitebox)"]
        ]))

# Обработчик для расчета дизайна
@dp.message_handler(lambda message: message.text in ["Новостройка (бетон)", "Новостройка (whitebox)"])
async def process_design_base(message: types.Message):
    user_data[message.from_user.id]["base"] = message.text
    await message.answer("Выберите услугу для дизайна:", reply_markup=types.ReplyKeyboardMarkup([
        ["Обмерный план", "3D коллажи", "Чертежи", "Планировочное решение", "3D визуализация"]
    ]))

# Обработчик для услуг дизайна
@dp.message_handler(lambda message: message.text in ["Обмерный план", "3D коллажи", "Чертежи", "Планировочное решение", "3D визуализация"])
async def process_design_services(message: types.Message):
    service = message.text
    if service == 'Обмерный план':
        user_data[message.from_user.id]["design_measurement"] = design_prices["Обмерный план"]
    elif service == '3D коллажи':
        user_data[message.from_user.id]["design_collages"] = design_prices["3D коллажи"]
    elif service == 'Чертежи':
        user_data[message.from_user.id]["design_drawings"] = design_prices["Чертежи"]
    elif service == 'Планировочное решение':
        user_data[message.from_user.id]["design_layout"] = design_prices["Планировочное решение"]
    elif service == '3D визуализация':
        user_data[message.from_user.id]["design_3d"] = design_prices["3D визуализация"]

    await message.answer("Услуга добавлена. Хотите добавить еще услуги для расчёта?\n1. Да\n2. Нет", reply_markup=types.ReplyKeyboardMarkup([
        ["Да", "Нет"]
    ]))

# Обработчик для завершения выбора услуг дизайна
@dp.message_handler(lambda message: message.text == "Нет")
async def finish_design_services(message: types.Message):
    total_design_cost = sum(user_data[message.from_user.id].get(key, 0) for key in ["design_measurement", "design_collages", "design_drawings", "design_layout", "design_3d"])

    await message.answer(f"Итоговая стоимость дизайна: {total_design_cost} рублей")

    # Отправка отчета в группу
    group_id = "-1002528008430"  # ID группы
    await bot.send_message(group_id,
        f"Новый запрос по дизайну для {message.from_user.full_name} (ID: {message.from_user.id})\n"
        f"Услуги:\nОбмерный план: {user_data[message.from_user.id].get('design_measurement', 0)}\n"
        f"3D коллажи: {user_data[message.from_user.id].get('design_collages', 0)}\n"
        f"Чертежи: {user_data[message.from_user.id].get('design_drawings', 0)}\n"
        f"Планировочное решение: {user_data[message.from_user.id].get('design_layout', 0)}\n"
        f"3D визуализация: {user_data[message.from_user.id].get('design_3d', 0)}\n"
        f"Итоговая стоимость дизайна: {total_design_cost} рублей"
    )

    await bot.send_message(message.from_user.id, "Спасибо! Свяжитесь с нами для дальнейшего обсуждения.")

    # Кнопки для завершения и начала нового расчёта
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("Написать в личный Telegram", url="https://t.me/ariadnahome_pro")
    button2 = InlineKeyboardButton("Новый расчёт (Дизайн)", callback_data="design_calculation")
    keyboard.add(button1, button2)

    await message.answer("Вы можете начать новый расчёт или связаться с нами.", reply_markup=keyboard)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)