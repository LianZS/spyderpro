import time
import datetime
import calendar
import requests
import os
import csv
import re
import sys
import json
from queue import Queue
import threading
from queue import Queue
from urllib.parse import urlencode
from concurrent import futures
from spyderpro.portconnect.InternetConnect import Connect
from spyderpro.portconnect.ParamCheck import ParamTypeCheck


class PlaceInterface(Connect, ParamTypeCheck):
    instance = None
    instance_flag: bool = False

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    # 获取所有省份
    def get_allprovince(self) -> list:
        """
        获取所有省份
        :return: list
        """
        href = "https://heat.qq.com/api/getAllProvince.php?sub_domain="
        par: str = None
        g = self.connect(par, href)
        data = [value["province"] for value in g]
        return data

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
        获取城市下所有地区信息标识，关键id

        :type province: str
        :type city:str
        :param province:省份
        :param city:城市
        :return  list[{"place": , "id": },,,,]
        """
        self.type_check(province, str)
        self.type_check(city, str)
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
            placename = value['name']  # 地点
            placeid = value["id"]  # id
            dic = {"place": placename, "id": placeid}
            datalist.append(dic)
        return datalist
        # range表示数据间隔，最小1,region_name是地点名字,id是景区pid


class PlaceTrend(PlaceInterface):
    """获取位置流量趋势"""

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


class PlaceFlow(PlaceInterface):
    """
    获取地区人口分布情况数据
    """

    def __init__(self, user_agent: str = None):

        if not PlaceFlow.instance_flag:
            PlaceFlow.instance_flag = True
            self.headers = dict()
            if user_agent is None:
                self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 ' \
                                             '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

            else:
                self.headers['User-Agent'] = user_agent
            self.headers['Host'] = 'heat.qq.com'

            self.request = requests.Session()

    def request_heatdata(self, url: str):
        """
        网络请求
        :param url:
        :return:json
        """
        response = self.request.get(url=url, headers=self.headers)
        g = json.loads(response.text)
        return g

    def __get_heatdata_bytime(self, date: str, datetim: str, region_id: int):
        self.date_format_check(date)
        self.time_format_check(datetim)
        # self.type_check(region_id, int)
        paramer = {
            'region_id': region_id,
            'datetime': "".join([date, ' ', datetim]),
            'sub_domain': ''
        }
        url = "https://heat.qq.com/api/getHeatDataByTime.php?" + urlencode(paramer)
        g = self.request_heatdata(url)
        return g

    def count_headdata(self, date: str, datetim: str, region_id: int):

        """
        某一时刻的人数有多少
        :param date:日期：格式yyyy-mm-dd
        :param datetim:时间：格式hh:MM:SS
        :param region_id:地区唯一表示
        :return:总人数
        """

        g = self.__get_heatdata_bytime(date, datetim, region_id)
        count = sum(g.values())  # 总人数
        return {"date": "".join([date, ' ', datetim]), "num": count}

    def complete_heatdata(self, date: str, datetim: str, region_id: int):
        """
           某一时刻的人数以及分布情况
           :param date:日期：格式yyyy-mm-dd
           :param datetime:时间：格式hh:MM:SS
           :param region_id:地区唯一表示
           :return:dict格式：{"lat": lat, "lng": lng, "num": num}->与中心经纬度的距离与相应人数
           """
        g = self.__get_heatdata_bytime(date, datetim, region_id)
        coords = map(self.deal_coordinates, g.keys())  # 围绕中心经纬度加减向四周扩展
        numlist = iter(g.values())
        for xy, num in zip(coords, numlist):
            lat = xy[0]
            lng = xy[1]
            yield {"lat": lat, "lng": lng, "num": num}

    @staticmethod
    def deal_coordinates(coord):
        if coord == ',':
            return (0, 0)
        escape = eval(coord)

        return escape

    def date_format_check(self, param):
        check = re.match("^\d{4}-\d{2}-\d{2}$", param)

        self.type_check(check, re.Match)

    def time_format_check(self, param):
        check = re.match("^\d{2}:\d{2}:\d{2}$", param)

        self.type_check(check, re.Match)

class CeleryThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        threading.Thread.__init__(self)
        self._target = target
        self._args = args

    def run(self):
        result = self._target(*self._args)
        data_queue.put(result)
        semaphore.release()
def writeinfo():
    place = PlaceTrend()

    executor = futures.ThreadPoolExecutor(max_workers=4)
    provinces = place.get_allprovince()
    tasklist = executor.map(place.get_allcity, provinces)
    filepath = os.path.join(os.path.pardir, "testdata/region_id.csv")
    f = open(filepath, "a+", newline="")
    w = csv.writer(f)
    w.writerow(['地区', "id"])

    for task in tasklist:
        resultlist = executor.map(lambda value: place.get_regions_bycity(value['province'], value['city']), task)
        for result in resultlist:
            writeresult = map(lambda item: w.writerow([item['place'], item['id']]), result)
            set(writeresult)
    f.close()


if __name__ == "__main__":
    place = PlaceTrend(date_begin='2019-06-11', date_end='2019-06-13')
    semaphore = threading.Semaphore(6)  # 每次最多5个线程在执行
    data_queue = Queue(maxsize=10)
    result = place.get_allcity("广东省")
    for info in result:
        cityinfo = place.get_regions_bycity(info['province'], info['city'])
        for item in cityinfo:
            for i in place.getlocations(item['place'], item['id']):
                print(i)
            break
        exit(0)
