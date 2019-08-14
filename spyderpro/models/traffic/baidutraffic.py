import requests
import json
import time
from urllib.parse import urlencode
from typing import Dict, Iterator
from threading import Semaphore, Thread
from queue import Queue

from spyderpro.models.traffic.trafficinterface import Traffic
from spyderpro.instances.trafficclass import TrafficClass, Road, Year
from spyderpro.instances.infomation import CityInfo


class BaiduTraffic(Traffic):
    wait = Semaphore(5)  # 允许同时运行5个任务
    dataqueue = Queue(8)  # 存放数据队列
    quitcount = 10  # 记录任务是否完成了，完成了-1
    lock = Semaphore(1)  # 锁住-1操作

    def __init__(self):
        self.s = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/71.0.3578.98 Safari/537.36'

        }
        # 获取实时城市交通情况

    # def deco(func):
    #     def Load(self, cityCode):
    #         data = func(self, cityCode)
    #         return data
    #
    #     return Load
    #
    # @deco
    def citytraffic(self, citycode, timetype='minute') -> list:
        """获取实时交通状态，包括日期，拥堵指数，具体时刻

        :param citycode:城市id
        :param timetype:时间间隔单位，day 和minute，默认minute
        :return iterable(dict)
        dict->{'date': '2019-06-14', 'index': 1.49, 'detailTime': '14:00'}"""
        parameter = {
            'cityCode': citycode,
            'type': timetype
        }
        href = 'https://jiaotong.baidu.com/trafficindex/city/curve?' + urlencode(parameter)
        try:
            data = self.s.get(url=href, headers=self.headers)
            g = json.loads(data.text)
        except Exception as e:
            print("网络链接error:%s" % e)
            return None
        today = time.strftime("%Y-%m-%d", time.localtime())  # 今天的日期
        date = today
        if '00:00' in str(g):
            date = time.strftime("%Y-%m-%d", time.localtime(time.time() - 3600 * 24))  # 昨天的日期
        # 含有24小时的数据
        for item in g['data']['list']:
            # {'index': '1.56', 'speed': '32.83', 'time': '13:45'}
            if item["time"] == '00:00':
                date = today
            ddate = int(date.replace("-", ""))  # 日期
            iindex = float(item['index'])  # 拥堵指数
            detailtime = item['time'] + ":00"  # 具体时刻
            yield TrafficClass(citycode, ddate, iindex, detailtime)

    def yeartraffic(self, citycode: int, year: int = int(time.strftime("%Y", time.localtime())),
                    quarter: int = int(time.strftime("%m", time.localtime())) / 3) -> Iterator[Road]:
        """
        获取城市年度交通数据
        :param citycode: 城市id
        :param year: 年份
        :param quarter: 第几季度
        :return: iterable(dict)
        dict->{"date": date, "index": index, "city": name} """

        parameter = {
            'cityCode': citycode,
            'type': 'day'  # 有分钟也有day
        }
        href = 'https://jiaotong.baidu.com/trafficindex/city/curve?' + urlencode(parameter)

        try:
            data = self.s.get(url=href, headers=self.headers)
            obj = json.loads(data.text)
        except Exception as e:
            print("百度年度交通爬取失败！:%s" % e)
            return None
        if not len(obj):
            return None
        year = time.strftime("%Y-", time.localtime())  # 年份

        for item in obj['data']['list']:
            # {'index': '1.56', 'speed': '32.83', 'time': '04-12'}
            date = year + item['time']
            index = float(item["index"])
            yield Year(pid=citycode, date=int(date.replace("-", "")), index=index)

    def roaddata(self, citycode) -> Iterator[Road]:
        """
        获取拥堵道路前10名数据, 数据包括路名，速度，数据包，道路方向，道路经纬度数据

        :param citycode:城市id
        :return: iterable(dict)
        dict->{"RoadName": roadname, "Speed": speed, "Direction": direction, "Bounds": bounds, 'Data': data}
        """
        dic = self.__roads(citycode)
        if dic['status'] == 1:
            print("参数不合法")
            return None
        datalist = self.__realtime_road(dic, citycode)

        datalist = sorted(datalist, key=lambda x: x["num"])  # 数据必须排序，不然和下面的信息不对称
        for item, data in zip(dic['data']['list'], datalist):
            roadname = item["roadname"]
            speed = float(item["speed"])
            direction = item['semantic']
            bounds = json.dumps({"coords": data['coords']})
            data = json.dumps(data['data'])
            num = eval(data)['num']
            rate =float(item['index'])
            road = Road(pid=citycode, roadname=roadname, speed=speed, dircetion=direction, bounds=bounds, data=data,
                        num=num,rate=rate)
            yield road

    def __roads(self, citycode) -> json:
        """
        获取道路信息包，包括道路pid，道路名，道路方向，速度
        :param citycode:城市id
        :return:dict
        """
        parameter = {
            'cityCode': citycode,
            'roadtype': 0
        }
        href = ' https://jiaotong.baidu.com/trafficindex/city/roadrank?' + urlencode(parameter)
        data = self.s.get(url=href, headers=self.headers)
        dic = json.loads(data.text)
        return dic

    def __realtime_road(self, dic, citycode) -> Iterator[Dict]:
        """
           处理10条道路路实时路况数据
           :param dic:
           :param citycode:
           :return: dict
           """
        for item, i in zip(dic['data']['list'], range(10)):
            self.wait.acquire()
            Thread(target=self.__realtime_roaddata, args=(item['roadsegid'], i, citycode)).start()

        while self.quitcount:
            data = self.dataqueue.get()
            yield data

    # 道路请求
    def __realtime_roaddata(self, pid, i, citycode):
        """
         具体请求某条道路的数据
         :param pid:道路id
         :param citycode: 城市id
         :param i: 排名

         """
        parameter = {
            'cityCode': citycode,
            'id': pid
        }
        href = 'https://jiaotong.baidu.com/trafficindex/city/roadcurve?' + urlencode(parameter)
        try:
            data = self.s.get(url=href, headers=self.headers)
            obj = json.loads(data.text)
        except Exception as e:
            print(e)
            self.dataqueue.put({"data": None, "coords": None, "num": i})
            self.lock.acquire()
            self.quitcount -= 1
            self.lock.release()

            return
        timelist = []
        data = []
        for item in obj['data']['curve']:  # 交通数据
            timelist.append(item['datatime'])
            data.append(item['congestIndex'])
        realdata = {"num": i, "time": timelist, "data": data}
        bounds = []
        for item in obj['data']['location']:  # 卫星数据
            bound = {}
            for locations, count in zip(item.split(","), range(0, item.split(",").__len__())):
                if count % 2 != 0:

                    bound['lat'] = locations  # 纬度

                else:
                    bound['lon'] = locations  # 纬度
            bounds.append(bound)
        self.dataqueue.put({"data": realdata, "coords": bounds, "num": i})
        self.wait.release()
        self.lock.acquire()
        self.quitcount -= 1
        self.lock.release()

    def getallcitycode(self) -> Iterator[CityInfo]:
        """
        获取最新的交通基本信息，比如id，省份，位置等等等
        :return: list
        """
        url = "https://jiaotong.baidu.com/trafficindex/city/list?"
        response = self.s.get(url=url, headers=self.headers)
        g = json.loads(response.text)
        for value in g['data']['list']:
            citycode = value['citycode']  # id
            cityname = value['cityname']  # 城市名
            city_coords = value['city_coords']
            coords = eval(city_coords)
            lat = coords[1] / 100000  # 纬度
            lon = coords[0] / 100000  # 经度

            provincecode = value['provincecode']  # 省份id
            provincename = value['provincename']  # 省份
            yield CityInfo(provincename, provincecode, cityname, citycode, lat, lon)


