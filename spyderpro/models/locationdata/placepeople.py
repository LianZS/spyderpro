import time
import requests
import re
import json
from datetime import datetime, timedelta
import threading
from queue import Queue
from urllib.parse import urlencode
from typing import Iterator
from spyderpro.portconnect.internetconnect import Connect
from spyderpro.portconnect.paramchecks import ParamTypeCheck
from spyderpro.instances.lbs import Trend, Geographi, Positioning


class PlaceInterface(Connect, ParamTypeCheck):
    instance = None
    instance_flag: bool = False

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    # 获取所有省份
    def get_provinces(self) -> list:
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
    def get_citys(self, province: str) -> list:
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
            dic = {'city': city, "place": placename, "id": placeid}
            datalist.append(dic)
        return datalist
        # range表示数据间隔，最小1,region_name是地点名字,id是景区pid

    def get_bounds(self, pid: int):
        href = "https://heat.qq.com/api/getRegionHeatMapInfoById.php?id=" + str(pid)
        headers = dict()
        headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 ' \
                                '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        response = requests.get(url=href, headers=headers).text
        g = json.loads(response)
        bounds = g['boundary']
        center = g['center_gcj'].split(',', 2)
        lat = center[0]
        lon = center[1]
        return {"bounds": bounds, "lat": lat, "lon": lon}


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

    def get_trend(self, region_name: str, pid: int) -> Iterator[Trend]:
        """

        获取地点的位置流量趋势指数，返回list({地点, 日期，趋势列表},,,)
        :param region_name:  地名
        :param pid: 地点id

        :return  Iterator[Trend]
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

        '''获取间隔日期 ----仅限于最大周期15天'''
        intervallong = timedelta(minutes=5)
        starttime = datetime(2019, 1, 1, 0, 0, 0)
        for date in self.dateiter():
            for index, detailt in zip(g[date],
                                      [str((starttime + intervallong * i).time()) for i in range(len(g[date]))]):
                trend = Trend(place=region_name, date=int(date.replace("-", "")), index=index, detailtime=detailt)
                yield trend

    def dateiter(self) -> Iterator[str]:
        formatdate = time.strptime(self.date_begin, "%Y-%m-%d")
        intervallong = timedelta(days=1)
        date = datetime(formatdate.tm_year, formatdate.tm_mon, formatdate.tm_mday)
        while 1:
            d = str(date.date())
            if d == self.date_end:
                break
            yield d

            date = date + intervallong


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

    def request_heatdata(self, url: str) -> json:
        """
        网络请求
        :param url:
        :return:json
        pr

        """
        try:
            response = self.request.get(url=url, headers=self.headers)
        except Exception as  e:
            print(e)
            return None
        if response.status_code == 200:
            g = json.loads(response.text)
            return g
        else:
            return None

    def get_heatdata_bytime(self, date: str, datetim: str, region_id: int):
        """
        某一时刻的人口分布详情
        :param date:日期：格式yyyy-mm-dd
        :param dateTime:时间：格式hh:MM:SS
        :param region_id:地区唯一表示
        :return: json
        """
        self.date_format_check(date)
        self.time_format_check(datetim)
        self.type_check(region_id, int)
        paramer = {
            'region_id': region_id,
            'datetime': "".join([date, ' ', datetim]),
            'sub_domain': ''
        }
        # https://heat.qq.com/api/getHeatDataByTime.php?region_id=5381&datetime=2019-01-01+01%3A10%3A00&sub_domain=
        url = "https://heat.qq.com/api/getHeatDataByTime.php?" + urlencode(paramer)
        g = self.request_heatdata(url)
        return g

    def count_headdata(self, data: json, ddate: str, dateTime: str, region_id: int) -> Positioning:

        """
        某一时刻的人数有多少
        :param date:日期：格式yyyy-mm-dd
        :param dateTime:时间：格式hh:MM:SS
        :param region_id:地区唯一表示
        :return:总人数
        """

        g = data
        if not g:
            return Positioning(None, None, None, None)
        num = sum(g.values())  # 总人数
        positioning = Positioning(region_id=region_id, date=int(ddate.replace("-", "")), detailtime=dateTime, num=num)
        return positioning

    def complete_headata(self, g: json) -> Iterator[Geographi]:
        """ 某一时刻的人数以及分布情况的json格式
            :returnrn {"lat": lat, "lng": lng, "num": num}->与中心经纬度的距离与相应人数
        """
        coords = map(self.deal_coordinates, g.keys())  # 围绕中心经纬度加减向四周扩展
        numlist = iter(g.values())
        for xy, num in zip(coords, numlist):
            lat = xy[0]
            lng = xy[1]
            geographi = Geographi(latitude=float(lat) / 1000, longitude=float(lng) / 1000, number=int(num))
            yield geographi

    def complete_heatdata_simple(self, date: str, dateTime: str, region_id: int) -> Iterator[Geographi]:
        """
           某一时刻的人数以及分布情况
           :param date:日期：格式yyyy-mm-dd
           :param dateTime:时间：格式hh:MM:SS
           :param region_id:地区唯一表示
           :return:dict格式：{"lat": lat, "lng": lng, "num": num}->与中心经纬度的距离与相应人数
           """
        g = self.get_heatdata_bytime(date, dateTime, region_id)
        coords = map(self.deal_coordinates, g.keys())  # 围绕中心经纬度加减向四周扩展
        numlist = iter(g.values())
        for xy, num in zip(coords, numlist):
            lat = xy[0]
            lng = xy[1]
            geographi = Geographi(latitude=float(lat) / 1000, longitude=float(lng) / 1000, number=int(num))
            yield geographi

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


# class CeleryThread(threading.Thread):
#     def __init__(self, group=None, target=None, name=None,
#                  args=(), kwargs=None, *, daemon=None):
#         threading.Thread.__init__(self)
#         self._target = target
#         self._args = args
#
#     def run(self):
#         result = self._target(*self._args)
#         data_queue.put(result)
#         semaphore.release()


# def writeinfo():
#     place = PlaceTrend()
#
#     executor = futures.ThreadPoolExecutor(max_workers=4)
#     provinces = place.get_allprovince()
#     tasklist = executor.map(place.get_allcity, provinces)
#     filepath = os.path.join(os.path.pardir, "testdata/region_id.csv")
#     f = open(filepath, "a+", newline="")
#     w = csv.writer(f)
#     w.writerow(['地区', "id"])
#
#     for task in tasklist:
#         resultlist = executor.map(lambda value: place.get_regions_bycity(value['province'], value['city']), task)
#         for result in resultlist:
#             writeresult = map(lambda item: w.writerow([item['place'], item['id']]), result)
#             set(writeresult)
#     f.close()


if __name__ == "__main__":
    import csv

    # f = open('/Users/darkmoon/Project/SpyderPr/datafile/scenceinfo.csv', 'a+', newline='')
    # w = csv.writer(f)
    # w.writerow(['城市', '地名', '标识', '中心经度', '中心维度', "经纬度范围"])
    # p = PlaceFlow()
    # for province in PlaceFlow().get_provinces():
    #     for city in p.get_citys(province):
    #         city=city['city']
    #         for k in p.get_regions_bycity(province,city):
    #
    #             pid = k['id']
    #             area=k['place']
    #             response= p.get_bounds(pid)
    #             lon=response['lon']
    #             lat=response['lat']
    #             bounds = response['bounds']
    #             w.writerow([city,area,pid,lon,lat,bounds])
    #             f.flush()
    #
    # f.close()
    #

    # p = PlaceFlow().complete_heatdata('2019-06-01', "15:20:00", 6)
    #
    # place = PlaceTrend(date_begin='2019-06-11', date_end='2019-06-13')
    # semaphore = threading.Semaphore(6)  # 每次最多6个线程在执行
    # data_queue = Queue(maxsize=10)
    # result = place.get_citys("广东省")
    # for info in result:
    #     cityinfo = place.get_regions_bycity(info['province'], info['city'])
    #     for item in cityinfo:
    #         for i in place.get_trend(item['place'], item['id']):
    #             print(i)
    #         break
    # exit(0)
