from typing import Dict
from spyderpro.models.weather.airstate import AirState
class Weather:
    def get_city_weather_pid(self)->Dict:
        return AirState().get_city_air_pid()
    def last_air_state(self,citypid):

        return AirState().get_city_air_state(citypid)