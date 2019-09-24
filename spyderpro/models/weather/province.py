class WeatherOfProvinceLink:
    """
    省份天气入口
    """

    def __init__(self, province, url):
        self.province = province
        self.url = url

    def __str__(self):
        return "省份:{province}的天气数据入口为：{url}".format(province=self.province, url=self.url)


class WeatherOfCityLink:
    """
    城市天气入口
    """

    def __init__(self, city, url):
        self.city = city
        self.url = url

    def __str__(self):
        return "城市:{province}的天气数据入口为：{url}".format(province=self.city, url=self.url)
