class AQIState:
    """

    """

    def __init__(self, aqi, pm2, pm10, so2, no2, co, o3):
        self.aqi = aqi
        self.pm2 = pm2
        self.pm10 = pm10
        self.so2 = so2
        self.no2 = no2
        self.co = co
        self.o3 = o3

    def __str__(self):
        return "PM2.5：{pm2},PM10:{pm10},二氧化硫:{so2},二氧化氮:{no2},一氧化碳:{co},臭氧{o3},AQI:{aqi}".format(self.pm2,
                                                                                                 pm10=self.pm10,
                                                                                                 so2=self.so2,
                                                                                                 no2=self.no2,
                                                                                                 co=self.co,
                                                                                                 o3=self.o3,
                                                                                                 aqi=self.aqi)


class InfoOfCityOfAQI:
    """
    城市aqi入口pid信息
    """

    def __init__(self, city, aqi_pid):
        self.city = city
        self.aqi_pid = aqi_pid

    def __str__(self):
        return "城市：{city},的aqi标识是：{pid}".format(city=self.city, pid=self.aqi_pid,
                                                )
