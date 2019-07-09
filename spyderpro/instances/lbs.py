class Geographi:
    """
    {"纬度": latitude, "经度": longitude, "人数": number}
    """
    __slots__ = ['longitude', 'latitude', 'number']

    def __init__(self, latitude, longitude, number):
        self.longitude = longitude
        self.latitude = latitude
        self.number = number
