import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime
from pyowm.owm import OWM
from pyowm.utils import config, timestamps
from PyQt5.QtCore import Qt, QTimer


def to_fixed(num, digits=0):
    return float(f'{num:.{digits}f}')


name = str(random.randint(1000, 99999999999999))

config_dict = config.get_config_from('configs/owmconfig.json')

owmKey = OWM('c6514e4959626a2e6eca7fa05db91fc7', config_dict)

temp_graph = []
hours = [6, 9, 12, 15, 18, 21]


# ГЕНЕРАЦИЯ ТАБЛИЦЫ
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


