from typing import SupportsInt


class Trend:
    """.
    地区人口趋势
    { place:地区名,date:日期,data：日趋势数据 }
    """
    __slots__ = ['place', 'ddate', "index", "detailtime", "region_id"]

    def __init__(self, pid: int, place: str, date: int, index: float, detailtime: str):
        self.region_id: int = pid
        self.place: str = place
        self.ddate: int = date
        self.index: float = index
        self.detailtime: str = detailtime

    def __str__(self):
        return "Trend----标识：{4}，地区名:{0},日期:{1},时间:{2},日趋势数据:{3}".format(self.place, self.ddate, self.detailtime,
                                                                        self.index, self.region_id)


class Geographi:
    """
    {"纬度": latitude, "经度": longitude, "人数": number}
    """
    __slots__ = ['longitude', 'latitude', 'number']

    def __init__(self, latitude, longitude, number):
        self.longitude = longitude
        self.latitude = latitude
        self.number = number

    def __str__(self):
        return "Geographi： 维度：{0},经度:{1}，人数:{2}".format(self.latitude, self.longitude, self.number)


class Positioning:
    """
    地区定位数据
    {'日期'：date,'时刻'：detailTime，"数量":num,"地区标识":region_id}
    """
    __slots__ = ['region_id', 'date', 'detailTime', 'num']

    def __init__(self, region_id, date, detailtime, num):
        self.region_id: int = region_id
        self.date: int = date
        self.detailTime: str = detailtime
        self.num: int = num

    def __str__(self):
        return "Positioning:标识:{0},日期:{1},具体时间:{2},数量:{3}".format(self.region_id, self.date, self.detailTime,
                                                                  self.num)
