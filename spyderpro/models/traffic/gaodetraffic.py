import requests
import json
import time
from urllib.parse import urlencode
from typing import Iterator
from threading import Semaphore, Thread
from queue import Queue
from spyderpro.models.traffic.multhread import MulitThread
from spyderpro.models.traffic.trafficinterface import Traffic
from spyderpro.instances.trafficclass import TrafficClass, Road, Year


class GaodeTraffic(Traffic):
    wait = Semaphore(5)  # 允许同时运行5个任务
    dataqueue = Queue(8)  # 存放数据队列
    quitcount = 10  # 记录任务是否完成了，完成了-1
    lock = Semaphore(1)  # 锁住-1操作

    def __init__(self):
        self.s = requests.Session()
        self.headers = {
            'Host': 'report.amap.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/71.0.3578.98 Safari/537.36'

        }

    # def deco(func):
    #     def load(self, cityCode):
    #         data = func(self, cityCode)
    #         return data
    #
    #     return load
    #
    # @deco
    def citytraffic(self, citycode: int) -> Iterator[TrafficClass]:

        """获取实时交通状态，包括日期，拥堵指数，具体时刻
        Args:

          citycode:城市id
        Yields::
            返回TrafficClass类实例

        """
        url = "http://report.amap.com/ajax/cityHourly.do?cityCode=" + str(citycode)

        try:
            data = self.s.get(url=url, headers=self.headers)
            g = json.loads(data.text)
        except Exception as e:

            print("编号%d--网络链接error:%s" % (citycode, e))

            return None
        today = time.strftime("%Y-%m-%d", time.localtime())  # 今天的日期

        yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 3600 * 24))  # 昨天的日期
        date = yesterday
        # 含有24小时的数据
        for item in g:
            detailtime = time.strftime("%H:%M", time.localtime(int(item[0]) / 1000))
            if detailtime == '00:00':
                date = today

            ddate = int(date.replace("-", ""))  # 日期
            iindex = float(item[1])  # 拥堵指数
            detailtime = detailtime + ":00"  # 具体时刻
            yield TrafficClass(citycode, ddate, iindex, detailtime)

    # 道路数据获取
    def roaddata(self, citycode: int) -> Iterator[Road]:
        """
        获取拥堵道路前10名数据, 数据包括路名，速度，数据包，道路方向，道路经纬度数据

        :param citycode:城市id
        :return: iterable(dict)
        dict->{"RoadName": roadname, "Speed": speed, "Direction": direction, "Bounds": bounds, 'Data': data}
        """
        dic = self.__roads(citycode)  # 道路基本信息
        if not len(dic['route']):
            print("参数不合法或者网络链接失败")
            return None

        datalist = self.__realtimeroad(dic, citycode)  # 获取数据
        datalist = sorted(datalist, key=lambda x: x["num"])  # 数据必须排序，不然和下面的信息不对称

        for item, data in zip(dic['route'], datalist):
            roadname = item["name"]  # 路名
            speed = float(item["speed"])  # 速度
            data = json.dumps(data['data'])  # 数据包
            direction = item['dir']  # 道路方向
            bounds = json.dumps({"coords": item['coords']})  # 道路经纬度数据
            road = Road(pid=citycode, roadname=roadname, speed=speed, dircetion=direction, bounds=bounds, data=data)

            yield road

    def __roads(self, citycode: int) -> dict:
        """
        获取道路信息包，包括道路pid，道路名，道路方向，速度
        :param citycode:城市id
        :return:dict
        """

        req = {
            "roadType": 0,
            "timeType": 0,
            "cityCode": citycode
        }
        url = "https://report.amap.com/ajax/roadRank.do?" + urlencode(req)
        data = self.s.get(url=url, headers=self.headers)

        try:
            route = json.loads(data.text)  # 道路信息包
        except Exception as e:
            print(e)
            return {}
        list_id = []  # 记录道路pid
        list_roadname = []  # 记录道路名
        list_dir = []  # 记录道路方向
        list_speed = []  # 记录速度
        for item in route["tableData"]:
            list_roadname.append(item["name"])  # 道路名
            list_dir.append(item["dir"])  # 方向
            list_speed.append(item["speed"])  # 速度
            list_id.append(item["id"])  # 道路pid
        dic_collections = dict()  # 存放所有数据
        dic_collections["route"] = route['tableData']
        dic_collections["listId"] = list_id
        dic_collections["listRoadName"] = list_roadname
        dic_collections["listDir"] = list_dir
        dic_collections["listSpeed"] = list_speed

        return dic_collections

    def __realtimeroad(self, dic: dict, citycode: int) -> Iterator[dict]:
        """
        请求10条道路路实时路况数据
        :param dic:
        :param citycode:
        :return: dict
        """
        req = {
            "roadType": 0,
            "timeType": 0,
            "cityCode": citycode,
            'lineCode': ''

        }
        url = "https://report.amap.com/ajax/roadDetail.do?" + urlencode(req)

        for pid, i in zip(dic["listId"],
                          range(0, (dic["listId"]).__len__())):
            roadurl = url + str(pid)
            self.wait.acquire()
            Thread(target=self.__realtime_roaddata, args=(roadurl, i,)).start()
        while self.quitcount:
            data = self.dataqueue.get()
            yield data

    def __realtime_roaddata(self, roadurl, i):
        """
        具体请求某条道路的数据
        :param roadurl: 道路数据链接
        :param i: 排名
        :return: dict->{"num": i, "time": time_list, "data": data}

        """

        try:
            data = self.s.get(url=roadurl, headers=self.headers)
            g = json.loads(data.text)  # 拥堵指数
        except Exception as e:
            print(e)
            self.dataqueue.put({"data": None, "num": i})
            self.lock.acquire()
            self.quitcount -= 1
            self.lock.release()
            return
        data = []  # 拥堵指数
        time_list = []  # 时间
        for item in g:
            time_list.append(time.strftime("%H:%M", time.strptime(time.ctime(int(item[0] / 1000 + 3600 * 8)))))
            data.append(item[1])
        # {排名，时间，交通数据}
        realdata = {"num": i, "time": time_list, "data": data}
        self.dataqueue.put({"data": realdata, "num": i})
        self.wait.release()
        self.lock.acquire()
        self.quitcount -= 1
        self.lock.release()
        return

    def yeartraffic(self, citycode: int, year: int = int(time.strftime("%Y", time.localtime())),
                    quarter: int = int(time.strftime("%m", time.localtime())) / 3) -> Iterator[Year]:
        """
        获取城市年度交通数据
        :param citycode: 城市id
        :param name: 城市名
        :param year: 年份
        :param quarter: 第几季度
        :return: iterable(dict)
        dict->{"date": date, "index": index, "city": name}
        """
        if quarter - int(quarter) > 0:

            quarter = int(quarter) + 1
        else:
            quarter = int(quarter)
        url = "http://report.amap.com/ajax/cityDailyQuarterly.do?"

        # year键表示哪一年 的数据
        req = {
            "cityCode": citycode,
            "year": year,  # 年份
            "quarter": quarter  # 第几季
        }

        url = url + urlencode(req)

        try:
            data = self.s.get(url=url, headers=self.headers)
            g = eval(data.text)
        except SyntaxError:
            print("高德地图年度数据请求失败！")
            return None
        for date, index in zip(g["categories"], g['serieData']):
            yield Year(pid=citycode, date=int(date.replace("-", "")), index=index)
