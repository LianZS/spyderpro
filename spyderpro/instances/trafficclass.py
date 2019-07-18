class TrafficClass:
    __slots__ = ['date', 'index', 'detailtime']

    def __init__(self, ddate, iindex, detailtime):
        self.date: int = ddate
        self.index: float = iindex
        self.detailtime: str = detailtime

    def __str__(self):
        return "日期：{0}，时间：{1}，指数{2}".format(self.date, self.detailtime, self.index)


class Road:
    __slots__ = ['roadname', 'speed', 'direction', 'bounds', 'data']

    def __init__(self, roadname, speed, dircetion, bounds, data):
        self.roadname = roadname
        self.speed = speed
        self.direction = dircetion
        self.bounds = bounds
        self.data = data

    def __str__(self):
        return "路名：{0}，方向：{1}，速度：{2}，经纬度；{3}，指数集：{3}".format(self.roadname, self.direction, self.speed, self.bounds,
                                                             self.data)


class Year:
    __slots__ = ['date', 'index']

    def __init__(self, date: int, index: float):
        self.date = date
        self.index = index
