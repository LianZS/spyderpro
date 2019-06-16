import time
import datetime
import calendar
import requests
from spyderpro.Connect.InternetConnect import Connect
from urllib.parse import urlencode


class PlaceTrend(Connect):
    """获取位置流量趋势"""
    instance = None
    instance_flag: bool = False

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, date_begin: str = None, date_end: str = None, intervallong: int = 1, user_agent: str = None):
        """
        时间段最长15天，最小时间间隔是1分钟range，开始时间最早2016-07-18
        :type date_begin: str
        :type date_end:str
        :type intervallong:int
        :param intervallong:数据间隔时间，最小为1分钟

        :param date_begin:开始搜索时间
        :param date_end:结束搜索时间
        """
        self.date_begin = date_begin
        self.date_end = date_end
        self.intervallong = intervallong
        if not PlaceTrend.instance_flag:
            PlaceTrend.instance_flag = True
            self.headers = dict()
            if user_agent is None:
                self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 ' \
                                             '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

            else:
                self.headers['User-Agent'] = user_agent
            self.headers['Host'] = 'heat.qq.com'

            self.request = requests.Session()

    # 获取所有省份
    def get_allprovince(self) -> list:
        """
        获取所有省份
        :return: list
        """
        href = "https://heat.qq.com/api/getAllProvince.php?sub_domain="
        par: str = None
        g = self.connect(par, href)
        result = [value["province"] for value in g]
        return result

    # 所有城市
    def get_allcity(self, province: str) -> list:
        """
        获取省份下所有城市
        :param province: 省份名
        :return: list[{"province": , "city":}，，]
        """
        # 这里不需要quote中文转url，因为后面的urlencode自动会转

        parameter = {
            "province": province,
            "sub_domain": ''
        }
        href = "https://heat.qq.com/api/getCitysByProvince.php?" + urlencode(parameter)
        par: str = None
        g = self.connect(par, href)
        results = [{"province": province, "city": value["city"]} for value in g]
        return results

    def get_regions_bycity(self, province: str, city: str) -> list:
        """
        获取城市下所有景点信息

        :type province: str
        :type city:str
        :param province:省份
        :param city:城市
        :return  list[{"place": , "id": },,,,]
        """
        assert isinstance(province, str)
        assert isinstance(city, str)
        parameter = {
            'province': province,
            'city': city,
            'sub_domain': ''
        }

        href = "https://heat.qq.com/api/getRegionsByCity.php?" + urlencode(parameter)

        par: str = None
        g = self.connect(par, href)
        datalist = list()
        for value in g:
            placename = value['name']  # 景点
            placeid = value["id"]  # id
            dic = {"place": placename, "id": placeid}
            datalist.append(dic)
        return datalist
        # range表示数据间隔，最小1,region_name是地点名字,id是景区pid

    def getlocations(self, region_name: str, pid: int):
        """
        获取地点的位置流量趋势指数，返回list({地点, 日期，趋势列表},,,)
        :param region_name:  地点
        :param pid: 地点id

        :return  list[{"place": region_name, "date": date, "data": g[date]},,,,,]
        """
        parameter = {
            'region': pid,
            'date_begin': self.date_begin,
            'date_end': self.date_end,
            'range': self.intervallong,
            'predict': False  # 是否获取预测数据,若为true，预测那天的键需要加上「预测」两字
        }

        href = "https://heat.qq.com/api/getLocation_uv_percent_new.php?" + urlencode(parameter)
        par: str = None
        g = self.connect(par, href)
        start = time.strptime(self.date_begin, "%Y-%m-%d")
        end = time.strptime(self.date_end, "%Y-%m-%d")
        # interval    间隔天数

        '''获取间隔日期 ----仅限于最大周期15天'''
        datelist = []  # 计算保存日期列表---作为键来获取数据
        if not end.tm_year - start.tm_year:  # 同一年
            interval: int = end.tm_yday - start.tm_yday
            startday: int = start.tm_mday
            if not end.tm_mon - start.tm_mon:  # 同一月
                [datelist.append(date.isoformat()) for date in  # 获取时间列表
                 [datetime.date(start.tm_year, start.tm_mon, startday + day) for day in range(0, interval)]]
            else:
                monthdays: int = calendar.monthrange(start.tm_year, start.tm_mon)[1]  # 本月日数
                critical: int = monthdays - start.tm_mday  # 本月剩下几天
                l1: list = [datetime.date(start.tm_year, start.tm_mon, startday + day) for day in range(0, interval + 1)
                            if
                            day <= critical]
                l2: list = [
                    datetime.date(start.tm_year, end.tm_mon, day) for day in range(1, interval - critical)]
                l1.extend(l2)
                [datelist.append(date.isoformat()) for date in l1]

        else:  # 跨年
            interval = end.tm_mday + 31 - start.tm_mday
            startday = start.tm_mday
            critical = 31 - start.tm_mday  # 本月剩下几天
            l1 = [datetime.date(start.tm_year, start.tm_mon, startday + day) for day in range(0, interval + 1) if
                  day <= critical]
            l2 = [
                datetime.date(end.tm_year, end.tm_mon, day) for day in range(1, interval - critical)]
            l1.extend(l2)
            [datelist.append(date.isoformat()) for date in l1]
        assert len(datelist) < 15, " time interval is must  less than 15 day"
        for date in datelist:
            yield {"place": region_name, "date": date, "data": g[date]}


if __name__ == "__main__":
    place = PlaceTrend(date_begin='2019-06-11', date_end='2019-06-13')
    result = place.get_allcity("广东省")
    for info in result:
        cityinfo = place.get_regions_bycity(info['province'], info['city'])
        for item in cityinfo:
            for i in place.getlocations(item['place'], item['id']):
                print(i)
            break
        exit(0)
