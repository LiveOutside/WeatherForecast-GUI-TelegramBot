import sys
from datetime import datetime
from pyowm.owm import OWM
from pyowm.utils import config, timestamps
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QTimer


# GLOBAL_STATE = 0


def to_fixed(num, digits=0):
    return f'{num:.{digits}f}'


City = input('Введите город: ')

Weather_Conditions = {
    'clouds': 'icons/cloudy.png',
    'rain': 'icons/rain.png',
    'drizzle': 'icons/drizzle.png',
    'mist': 'icons/fog.png',
    'smoke': 'icons/fog.png',
    'haze': 'icons/fog.png',
    'dust': 'icons/fog.png',
    'sand': 'icons/fog.png',
    'ash': 'icons/fog.png',
    'squall': 'icons/fog.png',
    'tornado': 'icons/tornado.png',
    'thunderstorm': 'icons/thunder.png',
    'snow': 'icons/snow.png',
}

night = [0, 1, 2, 3, 4, 5, 6]

config_dict = config.get_config_from('configs/owmconfig.json')

owmKey = OWM('c6514e4959626a2e6eca7fa05db91fc7', config_dict)


class WeatherForecast(QMainWindow):
    def __init__(self):
        super(WeatherForecast, self).__init__()
        uic.loadUi('uics/WeatherForecastReady.ui', self)

        #self.button_maximize.clicked.connect(lambda: maximize_restore())
        self.button_minimize.clicked.connect(lambda: self.showMinimized())
        self.button_close.clicked.connect(lambda: self.close())

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.get_forecast()
        self.qTimer = QTimer()
        self.qTimer.setInterval(300000)
        self.qTimer.timeout.connect(self.renew_info)
        self.qTimer.start()

        def window_move(event):
            if event.buttons() == Qt.MouseButton.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        self.title_bar.mouseMoveEvent = window_move

    def get_forecast(self):

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
        # NEXT TOMORROW INFO
        if to_fixed(temperature_next_three_hours, 1) == '0.0':
            self.tomorrow_temperature_label.setText('0°')
        else:
            self.tomorrow_temperature_label.setText(str(to_fixed(temperature_tomorrow, 1)) + '°')

        # STATUS НА СЕГОДНЯ
        if weather_status.lower() in Weather_Conditions:
            self.main_image_label.setPixmap(QtGui.QPixmap(Weather_Conditions[weather_status.lower()]))

        elif weather_status.lower() == 'clear':
            if int(datetime.now().hour - 2) in night:
                self.main_image_label.setPixmap(QtGui.QPixmap('icons/night/moon.png'))
            else:
                self.main_image_label.setPixmap(QtGui.QPixmap('icons/day/sun.png'))

        # STATUS НА 3 ЧАСА ВПЕРЁД
        if next_three_hours_status.lower() in Weather_Conditions:
            self.next_three_hours_image_label.setPixmap(
                QtGui.QPixmap(Weather_Conditions[next_three_hours_status.lower()]))

        elif next_three_hours_status.lower() == 'clear':
            if int(datetime.now().hour - 2) in night:
                self.next_three_hours_image_label.setPixmap(QtGui.QPixmap('icons/night/moon.png'))
            else:
                self.next_three_hours_image_label.setPixmap(QtGui.QPixmap('icons/day/sun.png'))

        # STATUS НА ЗАВТРА
        if tomorrow_status.lower() in Weather_Conditions:
            self.tomorrow_image_label.setPixmap(QtGui.QPixmap(Weather_Conditions[tomorrow_status.lower()]))

        elif tomorrow_status.lower() == 'clear':
            self.tomorrow_image_label.setPixmap(QtGui.QPixmap('icons/day/sun.png'))

        # ДЛЯ ПРОВЕРКИ
        print(
            f'В городе {City}, температура {temperature}, ощущается как {feels_like_temperature}, минимальная {min_temperature}, максимальная {max_temperature}. '
            f'Влажность: {humidity}, скосроть ветра {wind_speed}, облачность {clouds}, давление {pressure}'
            f'статус погоды {weather_status}, детальный статус погоды {detailed_weather_status}')
        print(f'через 3 часа: {temperature_next_three_hours}, {next_three_hours_status} \n'
              f'завтра: {temperature_tomorrow}, {tomorrow_status}')
        print(int(datetime.now().hour) in night)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    # ОБНОВЛЕНИЕ ДАННЫХ В GUI С РАЗРЫВОМ В 30 МИНУТ
    def renew_info(self):
        self.get_forecast()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = WeatherForecast()
    win.setFixedWidth(380)
    win.setFixedHeight(700)
    win.show()
    sys.exit(app.exec())
