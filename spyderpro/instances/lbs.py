class Trend:
    __slots__ = ['place','date',"data"]
    def __init__(self):
        pass


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
        return "Geographi----维度：{0},经度:{1}，人数:{2}".format(self.latitude, self.longitude, self.number)


class Positioning:
    """
    地区定位数据
    {'日期'：date,'时刻'：detailTime，"数量":num,"地区标识":region_id}
    """
    __slots__ = ['region_id', 'date', 'detailTime', 'num']

    def __init__(self, region_id, date, detailtime, num):
        self.region_id = region_id
        self.date = date
        self.detailTime = detailtime
        self.num = num

    def __str__(self):
        return "Positioning:标识:{0}--日期:{1},具体时间:{2},数量:{3}".format(self.region_id, self.date, self.detailTime,
                                                                   self.num)
