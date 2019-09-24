from typing import Iterator
from spyderpro.models.weather.airstate import AirState
from spyderpro.models.weather.aqi import AQIState, InfoOfCityOfAQI



class Weather:
    def get_city_weather_pid(self) -> Iterator[InfoOfCityOfAQI]:
        return AirState().get_city_air_pid()

    def last_air_state(self, citypid)->AQIState:
        return AirState().get_city_air_state(citypid)
