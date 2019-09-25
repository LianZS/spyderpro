from .celeryconfig import app
from spyderpro.manager_function.manager_weather import ManagerWeather

@app.task(queue='weather')
def monitoring_weather_state():
    """
    监控天气状态

    """
    ManagerWeather().manager_city_airstate()
