class AQIState:
    __slots__ = ['aqi', "pm2", "pm10", "so2", "no2", "co", "o3"]

    def __init__(self, aqi, pm2, pm10, so2, no2, co, o3):
        self.aqi = aqi
        self.pm2 = pm2
        self.pm10 = pm10
        self.so2 = so2
        self.no2 = no2
        self.co = co
        self.o3 = o3

    def __str__(self):
        return "PM2.5：{0},PM10:{1},二氧化硫:{2},二氧化氮:{3},一氧化碳:{4},臭氧{5},AQI:{6}".format(self.pm2, self.pm10,
                                                                                    self.so2,
                                                                                    self.no2, self.co, self.o3)
