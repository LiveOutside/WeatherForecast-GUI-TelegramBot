# Weather **Forecast**
## ⚫ **Libraries**
- *Pyowm*
- *PyQt5*
- *Aiogram*
- *Matplotlib*
- *Sqlite3*
- *Sys*
- *Numpy*
- *Datetime*
- *Random*
- *Logging*
## ⚫ **Main code (Code.py)**
- ### Connecting with GUI / Deleting Frames
```py
class WeatherForecast(QMainWindow):
    def __init__(self):
        super(WeatherForecast, self).__init__()
        uic.loadUi('uics/WeatherForecastReady.ui', self)

        # Buttons of custom TitleBar
        self.button_minimize.clicked.connect(lambda: self.showMinimized())
        self.button_close.clicked.connect(lambda: self.close())

        # Making QMainWindow Framless
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Renewing info about recent weather (w/ interval - 30 min)
        self.get_forecast()
        self.qTimer = QTimer()
        self.qTimer.setInterval(300000)
        self.qTimer.timeout.connect(self.renew_info)
        self.qTimer.start()
    
    def renew_info(self):
        self.get_forecast()
```
![GUI](https://downloader.disk.yandex.ru/preview/c9f0cc33c1460b60c23775ee6a1d1fe6906cd45f0370963b49179be9f6d80ca8/6293acd5/V4yM9j8V2QbJWyrNPghO1Yw3WA5yEgJE2axHvgxsywCOhHD5XGlCt0_89e5Y4b2TS_flOGcPikKDyXah5sTz-A%3D%3D?uid=0&filename=%D1%87%D1%8F%D1%81%D1%87%D1%8F%D1%81.png&disposition=inline&hash=&limit=0&content_type=image%2Fpng&owner_uid=0&tknv=v2&size=2048x2048)
- ### Functions of moving - QMainWindow w/ Custom TitleBar
```py
        # Function for moving QMainWindow which contains custom TitleBar
        def window_move(event):
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        self.title_bar.mouseMoveEvent = window_move

        def mousePressEvent(self, event):
            self.dragPos = event.globalPos()

```
- ### Recieving weather forecast / setting icons -> GUI / adding values -> GUI
```py
    def get_forecast(self):

        # WEATHER FORECAST FOR TODAY
        Manager = owmKey.weather_manager()
        Observation = Manager.weather_at_place(City)
        Weather = Observation.weather

        # TEMPERATURE -> TODAY
        temperature_request = Weather.temperature('celsius')
        temperature = temperature_request['temp']
        feels_like_temperature = temperature_request['feels_like']
        max_temperature = temperature_request['temp_max']
        min_temperature = temperature_request['temp_min']
        # WEATHER CONDITIONS -> TODAY
        humidity = Weather.humidity
        wind_speed = Weather.wind()['speed']
        clouds = Weather.clouds
        weather_status = Weather.status
        detailed_weather_status = Weather.detailed_status
        pressure = Weather.pressure['press']

        # WEATHER FORECAST FOR TOMORROW
        tomorrow = timestamps.tomorrow(12, 0)
        forecast = Manager.forecast_at_place(City, '3h')
        forecast_tomorrow = forecast.get_weather_at(tomorrow)

        # TEMPREATURE -> TOMORROW
        temperature_tomorrow_request = forecast_tomorrow.temperature('celsius')
        temperature_tomorrow = temperature_tomorrow_request['temp']

        # WEATHER CONDITIONS -> TOMORROW
        tomorrow_status = forecast_tomorrow.status
        tomorrow_detailed_weather_status = forecast_tomorrow.detailed_status

        # WEATHER FORECAST FOR THE NEXT THREE HOURS
        today_next_three_hours = timestamps.next_three_hours()
        forecast_today_next_three_hours = forecast.get_weather_at(today_next_three_hours)

        # TEMPERATURE -> NEXT THREE HOURS
        temperature_next_three_hours_request = forecast_today_next_three_hours.temperature('celsius')
        temperature_next_three_hours = temperature_next_three_hours_request['temp']

        # WEATHER CONDITIONS -> NEXT THREE HOURS
        next_three_hours_status = forecast_today_next_three_hours.status
        next_three_hours_detailed_weather_status = forecast_today_next_three_hours.detailed_status

        # MAIN INFO
        self.temperature_label.setText(str(to_fixed(temperature, 1)) + '°')
        self.city_label.setText(City.capitalize())

        # ADDITIONAL INFO
        self.wind_label.setText(str(wind_speed) + ' м/с')
        self.humidity_label.setText(str(humidity))
        self.feels_like_label.setText(str(round(feels_like_temperature)) + '°')
        self.pressure_label.setText(str(pressure) + ' мм.')

        # NEXT 3 HOURS INFO
        time = f'{int(datetime.now().strftime("%H")) + 3}:{datetime.now().strftime("%M")}'
        self.next_three_hours_label.setText(f'Сегодня в {time}')
        if to_fixed(temperature_next_three_hours, 1) == '0.0':
            self.next_three_hours_temperature_label.setText('0°')
        else:
            self.next_three_hours_temperature_label.setText(str(to_fixed(temperature_next_three_hours, 1)) + '°')
        # TOMORROW INFO
        if to_fixed(temperature_tomorrow, 1) == '0.0':
            self.tomorrow_temperature_label.setText('0°')
        else:
            self.tomorrow_temperature_label.setText(str(to_fixed(temperature_tomorrow, 1)) + '°')

        # STATUS -> TODAY
        if weather_status.lower() in Weather_Conditions:
            self.main_image_label.setPixmap(QtGui.QPixmap(Weather_Conditions[weather_status.lower()]))

        elif weather_status.lower() == 'clear':
            if int(datetime.now().hour - 2) in night:
                self.main_image_label.setPixmap(QtGui.QPixmap('icons/night/moon.png'))
            else:
                self.main_image_label.setPixmap(QtGui.QPixmap('icons/day/sun.png'))

        # STATUS -> NEXT THREE HOURS
        if next_three_hours_status.lower() in Weather_Conditions:
            self.next_three_hours_image_label.setPixmap(
                QtGui.QPixmap(Weather_Conditions[next_three_hours_status.lower()]))

        elif next_three_hours_status.lower() == 'clear':
            if int(datetime.now().hour - 2) in night:
                self.next_three_hours_image_label.setPixmap(QtGui.QPixmap('icons/night/moon.png'))
            else:
                self.next_three_hours_image_label.setPixmap(QtGui.QPixmap('icons/day/sun.png'))

        # STATUS -> TOMORROW
        if tomorrow_status.lower() in Weather_Conditions:
            self.tomorrow_image_label.setPixmap(QtGui.QPixmap(Weather_Conditions[tomorrow_status.lower()]))

        elif tomorrow_status.lower() == 'clear':
            self.tomorrow_image_label.setPixmap(QtGui.QPixmap('icons/day/sun.png'))
```
## ⚫ **Aiogram code (Telegram_bot.py) - Bot for Telegram**
- ### Bot initializing / menu
```py
# BOT INITIALIZING
weather_forecast_bot = Bot(token=TOKEN)
dp = Dispatcher(weather_forecast_bot)

# BUTTONS MENU
btnCredits = KeyboardButton('Информация о боте 👾')
btnSubscribe = KeyboardButton('Подписаться на рассылку 📩')
mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnCredits, btnSubscribe)
```
- ### Main bot commands / replies
```py
# START COMMAND
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await weather_forecast_bot.send_message(message.from_user.id,
                                            'Привет, {0}, введи /help для получения списка команд!'
                                            .format(message.from_user.first_name), reply_markup=mainMenu)


# ALL AVAILABLE COMMANDS
@dp.message_handler(commands=['help'])
async def start(message: types.Message):
    await weather_forecast_bot.send_message(message.from_user.id, '📄Список доступных команд:\n\n'
                                                                  'Вывод прогноза погоды для города\n'
                                                                  'Пример: Город -> Миасс\n'
                                                                  'Вывод графика температур на завтра\n'
                                                                  'Пример: График температур -> Миасс')


# ADDITIONAL INFO + MAILING + REPLY TO INPUT USERID ON A MESSAGE TYPE -> ('Город -> Миасс')
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

    # TEMPERATURE CHARTS -> MAIN.PY
    elif message.text.lower().startswith('график температур -> '):
        send_graph(message.text.split(' -> ')[1])
        try:
            await weather_forecast_bot.send_photo(chat_id=message.chat.id, photo=open(f'graphics/{name}.png', 'rb'))
        except:
            await weather_forecast_bot.send_message(message.from_user.id, 'Правильно введите название города! 🔴')

    # WEATHER CONDITIONS IN TOWN
    elif message.text.lower().startswith('город ->'):
        try:
            await weather_forecast_bot.send_message(message.from_user.id, get_forecast(message.text.split(' -> ')[1]))
        except:
            await weather_forecast_bot.send_message(message.from_user.id, 'Правильно введите название города! 🔴')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
```
## ⚫ **Charts code (main.py) - Charts for Telegram_bot.py**
```py
# CHART GENERATION FUNCTION (MATPLOTLIB)
def send_graph(City):
    global temp_graph
    manager = owmKey.weather_manager()
    observation = manager.weather_at_place(City)
    weather = observation.weather
    for hour in hours:
        tomorrow = timestamps.tomorrow(hour, 0)
        forecast = manager.forecast_at_place(City, '3h')
        forecast_tomorrow = forecast.get_weather_at(tomorrow)

        temperature_tomorrow_request = forecast_tomorrow.temperature('celsius')
        temperature_tomorrow = temperature_tomorrow_request['temp']
        temp_graph.append(to_fixed(temperature_tomorrow, 2))

    x = [to_fixed(hour, 2) for hour in hours]
    y = temp_graph

    plt.plot(x, y, label='Изменения в температуре на завтра')
    plt.xlabel('Время (Ч)')
    plt.ylabel('Температура (°C)')
    plt.legend(loc='lower right')
    plt.savefig(f'graphics/{name}.png')
    temp_graph = []
    x = []
    y = []
    plt.close()
```
