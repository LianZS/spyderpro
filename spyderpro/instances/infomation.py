class ScenceInfo:
    """
    景区基本信息
    """

    def __init__(self, province, city, area, longitude, latitude, bounds):
        self.province = province
        self.city = city
        self.area = area
        self.longitude = longitude
        self.latitude = latitude
        self.bounds = bounds


class CityInfo:
    __slots__ = ['provincename', 'provincecode', 'cityname', 'citycode', 'lat', 'lon']

    def __init__(self, provincename, provincecode, cityname, citycode, lat, lon):
        self.provincename = provincename# # 省份
        self.provincecode = provincecode
        self.cityname = cityname#城市名
        self.citycode = citycode
        self.lat = lat
        self.lon = lon
