import logging
import sqlite3
from main import send_graph, name
from configs.bot_config import TOKEN
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime
from pyowm.owm import OWM
from pyowm.utils import config, timestamps
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


sender_data_base = sqlite3.connect('configs/telegram_bot_data.db')
cursor = sender_data_base.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id TEXT
)""")

# ПОКА ЧТО БД НЕ ДОРАБОТАНА







def to_fixed(num, digits=0):
    return f'{num:.{digits}f}'


config_dict = config.get_config_from('configs/owmconfig.json')

owmKey = OWM('c6514e4959626a2e6eca7fa05db91fc7', config_dict)


def get_forecast(City):
    # ПРОГНОЗ ПОГОДЫ НА СЕГОДНЯ

    Manager = owmKey.weather_manager()
    Observation = Manager.weather_at_place(City)
    Weather = Observation.weather

    # ТЕМПЕРАТУРА
    temperature_request = Weather.temperature('celsius')
    temperature = temperature_request['temp']
    feels_like_temperature = temperature_request['feels_like']
    max_temperature = temperature_request['temp_max']
    min_temperature = temperature_request['temp_min']
    # СОСТОЯНИЕ ПОГОДЫ
    humidity = Weather.humidity
    wind_speed = Weather.wind()['speed']
    clouds = Weather.clouds
    weather_status = Weather.status
    detailed_weather_status = Weather.detailed_status
    pressure = Weather.pressure['press']

    # ПРОГНОЗ НА ЗАВТРА
    tomorrow = timestamps.tomorrow(12, 0)
    forecast = Manager.forecast_at_place(City, '3h')
    forecast_tomorrow = forecast.get_weather_at(tomorrow)

    # ТЕМПЕРАТУРА
    temperature_tomorrow_request = forecast_tomorrow.temperature('celsius')
    temperature_tomorrow = temperature_tomorrow_request['temp']

    # СОСТОЯНИЕ ПОГОДЫ
    tomorrow_status = forecast_tomorrow.status
    tomorrow_detailed_weather_status = forecast_tomorrow.detailed_status

    # ПРОГНОЗ НА 3 ЧАСА ВПЕРЁД
    today_next_three_hours = timestamps.next_three_hours()
    forecast_today_next_three_hours = forecast.get_weather_at(today_next_three_hours)

    # ТЕМПЕРАТУРА
    temperature_next_three_hours_request = forecast_today_next_three_hours.temperature('celsius')
    temperature_next_three_hours = temperature_next_three_hours_request['temp']

    # СОСТОЯНИЕ ПОГОДЫ
    next_three_hours_status = forecast_today_next_three_hours.status
    next_three_hours_detailed_weather_status = forecast_today_next_three_hours.detailed_status

    return f'В городе {City}:\n\nТемпература: {to_fixed(temperature, 1)}°,\n' \
           f'По ощущениям как: {to_fixed(feels_like_temperature, 1)}°,\n' \
           f'Минимальная температура: {to_fixed(min_temperature, 1)}°,\n' \
           f'Максимальная температура: {to_fixed(max_temperature, 1)}°,\n' \
           f'Температура через 3 часа: {to_fixed(temperature_next_three_hours, 1)}°,\n' \
           f'Температура завтра: {to_fixed(temperature_tomorrow, 1)}°,\n'\
           f'Влажность: {humidity}% 💧,\nСкороcть ветра - {wind_speed} м/с 💨,\nОблачность: {clouds} ☁,\n' \
           f'Давление: {pressure} мм. рт. ст 🌡,\n' \
           f'Состояние погоды: {detailed_weather_status.capitalize()}.'


# ДОП ИНФО
logging.basicConfig(level=logging.INFO)

# САМ БОТ
weather_forecast_bot = Bot(token=TOKEN)
dp = Dispatcher(weather_forecast_bot)

# MENU
btnCredits = KeyboardButton('Информация о боте 👾')
btnSubscribe = KeyboardButton('Подписаться на рассылку 📩')
mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnCredits, btnSubscribe)


# НАЧАЛО РАБОТЫ С БОТОМ
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await weather_forecast_bot.send_message(message.from_user.id,
                                            'Привет, {0}, введи /help для получения списка команд!'
                                            .format(message.from_user.first_name), reply_markup=mainMenu)


# ВЫВОД СПИСКА ДОСТУПНЫХ КОМАНД
@dp.message_handler(commands=['help'])
async def start(message: types.Message):
    await weather_forecast_bot.send_message(message.from_user.id, '📄Список доступных команд:\n\n'
                                                                  'Вывод прогноза погоды для города\n'
                                                                  'Пример: Город -> Миасс\n'
                                                                  'Вывод графика температур на завтра\n'
                                                                  'Пример: График температур -> Миасс')


# ADDITIONAL INFO + РАССЫЛКА + REPLY НА ВВОД USERID СООБЩЕНИЯ ПО ТИПУ ('Город -> Миасс')
@dp.message_handler()
async def bot_reply(message: types.Message):
    if message.text == 'Информация о боте 👾':
        await weather_forecast_bot.send_message(message.from_user.id, '🧾Доп. Информация:\n\n'
                                                                      'Бот создан: https://vk.com/lookaaatmeeee\n'
                                                                      'GitHub: https://github.com/LiveOutside\n'
                                                                      'Дата создания: 06.11.2021')
    elif message.text == 'Подписаться на рассылку 📩':
        await weather_forecast_bot.send_message(message.from_user.id,
                                                'Рассылка пока что не доступна, попробуйте записаться позже!')

    # ГРАФИКИ ТЕМПЕРАТУР MAIN.PY
    elif message.text.lower().startswith('график температур -> '):
        send_graph(message.text.split(' -> ')[1])
        try:
            await weather_forecast_bot.send_photo(chat_id=message.chat.id, photo=open(f'graphics/{name}.png', 'rb'))
        except:
            await weather_forecast_bot.send_message(message.from_user.id, 'Правильно введите название города! 🔴')

    # ВЫВОД СОСТОЯНИЯ ПОГОДНЫХ УСЛОВИЙ В ГОРОДЕ
    elif message.text.lower().startswith('город ->'):
        try:
            await weather_forecast_bot.send_message(message.from_user.id, get_forecast(message.text.split(' -> ')[1]))
        except:
            await weather_forecast_bot.send_message(message.from_user.id, 'Правильно введите название города! 🔴')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
