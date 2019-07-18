class TrafficClass:
    __slots__ = ['region_id', 'date', 'index', 'detailtime']

    def __init__(self, pid: int, ddate: int, iindex: float, detailtime):
        self.region_id: int = pid
        self.date: int = ddate
        self.index: float = iindex
        self.detailtime: str = detailtime

    def __str__(self):
        return "日期：{0}，时间：{1}，指数{2},标识{3}".format(self.date, self.detailtime, self.index, self.region_id)


class Road:
    __slots__ = ['region_id', 'roadname', 'speed', 'direction', 'bounds', 'data']

    def __init__(self, pid, roadname, speed, dircetion, bounds, data):
        self.region_id:int = pid
        self.roadname:str = roadname
        self.speed:float = speed
        self.direction:str = dircetion
        self.bounds:dict = bounds
        self.data :dict= data

    def __str__(self):
        return "标识{0},路名：{1}，方向：{2}，速度：{3}，经纬度；{4}，指数集：{5}".format(self.region_id, self.roadname, self.direction,
                                                                   self.speed, self.bounds,
                                                                   self.data)


class Year:
    __slots__ = ['region_id', 'date', 'index']

    def __init__(self, pid, date: int, index: float):
        self.region_id:int = pid
        self.date:int = date
        self.index:float = index
