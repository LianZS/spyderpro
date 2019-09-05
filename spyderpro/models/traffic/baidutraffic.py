import requests
import json
import time
from urllib.parse import urlencode
from typing import Dict, Iterator
from threading import Semaphore, Thread
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from spyderpro.models.traffic.trafficinterface import Traffic
from spyderpro.instances.trafficclass import TrafficClass, Road, Year
from spyderpro.instances.infomation import CityInfo


class BaiduTraffic(Traffic):

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
    def citytraffic(self, citycode: int, timetype='minute') -> Iterator[TrafficClass]:
        """获取实时交通状态，包括日期，拥堵指数，具体时刻

        :param citycode:城市id
        :param timetype:时间间隔单位，day 和minute，默认minute
        :return iterable(dict)
        dict->{'date': '2019-06-14', 'index': 1.49, 'detailTime': '14:00'}"""
        dict_parameter = {
            'cityCode': citycode,
            'type': timetype
        }
        str_href = 'https://jiaotong.baidu.com/trafficindex/city/curve?' + urlencode(dict_parameter)
        try:
            response = self.s.get(url=str_href, headers=self.headers)
            json_data = json.loads(response.text)
        except Exception as e:
            print("网络链接error:%s" % e)
            return []
        today_date = time.strftime("%Y-%m-%d", time.localtime())  # 今天的日期
        date = today_date
        if '00:00' in str(json_data):
            date = time.strftime("%Y-%m-%d", time.localtime(time.time() - 3600 * 24))  # 昨天的日期
        # 含有24小时的数据
        for item in json_data['data']['list']:
            # {'index': '1.56', 'speed': '32.83', 'time': '13:45'}
            if item["time"] == '00:00':  # 因为部分数据属于昨天的，所以日期需要区分
                date = today_date
            int_ddate = int(date.replace("-", ""))  # 日期
            float_iindex = float(item['index'])  # 拥堵指数
            str_detail_time = item['time'] + ":00"  # 具体时刻
            yield TrafficClass(citycode, int_ddate, float_iindex, str_detail_time)

    def yeartraffic(self, citycode: int, year: int = int(time.strftime("%Y", time.localtime())),
                    quarter: int = int(time.strftime("%m", time.localtime())) / 3) -> Iterator[Year]:
        """
        获取城市年度交通数据
        :param citycode: 城市id
        :param year: 年份
        :param quarter: 第几季度
        :return: iterable(dict)
        dict->{"date": date, "index": index, "city": name} """

        dict_parameter = {
            'cityCode': citycode,
            'type': 'day'  # 有分钟也有day
        }
        str_href = 'https://jiaotong.baidu.com/trafficindex/city/curve?' + urlencode(dict_parameter)

        try:
            response = self.s.get(url=str_href, headers=self.headers)
            obj = json.loads(response.text)
        except Exception as e:
            print("百度年度交通爬取失败！:%s" % e)
            return None
        if not len(obj):
            return None
        year = time.strftime("%Y-", time.localtime())  # 年份格式为2019-

        for item in obj['data']['list']:
            # {'index': '1.56', 'speed': '32.83', 'time': '04-12'}
            date = year + item['time']
            float_index = float(item["index"])
            yield Year(pid=citycode, date=int(date.replace("-", "")), index=float_index)

    def roaddata(self, citycode: int) -> Iterator[Road]:
        """
        获取拥堵道路前10名数据, 数据包括路名，速度，数据包，道路方向，道路经纬度数据

        :param citycode:城市id
        :return: iterable(Road)
        """
        # 请求道路数据, 获取道路信息包，包括道路pid，道路名，道路方向，速度

        json_road_data = self.__roads(citycode)
        if json_road_data['status'] == 1:
            print("参数不合法")
            return None
        datalist = self.__realtime_road(json_road_data, citycode)

        datalist = sorted(datalist, key=lambda x: x["num"])  # 数据必须排序，不然和下面的信息不对称
        for item, data in zip(json_road_data['data']['list'], datalist):
            roadname = item["roadname"]
            speed = float(item["speed"])
            direction = item['semantic']
            bounds = json.dumps({"coords": data['coords']})
            data = json.dumps(data['data'])
            num = eval(data)['num']
            rate = float(item['index'])
            road = Road(pid=citycode, roadname=roadname, speed=speed, dircetion=direction, bounds=bounds, data=data,
                        num=num, rate=rate)
            yield road

    def __roads(self, citycode) -> Dict:
        """
        获取道路信息包，包括道路pid，道路名，道路方向，速度
        :param citycode:城市id
        :return:dict
        """
        dict_parameter = {
            'cityCode': citycode,
            'roadtype': 0
        }
        str_href = ' https://jiaotong.baidu.com/trafficindex/city/roadrank?' + urlencode(dict_parameter)
        try:
            response = self.s.get(url=str_href, headers=self.headers)
        except ConnectionError:
            print("网络错误!")
            return {"status": 1}
        if response.status_code == 200:
            json_data = json.loads(response.text)
        else:
            json_data = {"status": 1}
        return json_data

    def __realtime_road(self, dic, citycode) -> Iterator[Dict]:
        """
           处理10条道路路实时路况数据
           :param dic:
           :param citycode:
           :return: dict
           """
        pool = ThreadPoolExecutor(max_workers=10)
        # 存放任务对象
        reuslt_list = list()
        for item, i in zip(dic['data']['list'], range(10)):
            t = pool.submit(self.__realtime_roaddata, item['roadsegid'], i, citycode)
            reuslt_list.append(t)
        for t in reuslt_list:
            # 返回结果
            yield t.result()

    # 道路请求
    def __realtime_roaddata(self, pid, i, citycode) -> Dict:
        """
         具体请求某条道路的数据
         :param pid:道路id
         :param citycode: 城市id
         :param i: 排名

         """
        dict_parameter = {
            'cityCode': citycode,
            'id': pid
        }
        str_href = 'https://jiaotong.baidu.com/trafficindex/city/roadcurve?' + urlencode(dict_parameter)
        try:
            data = self.s.get(url=str_href, headers=self.headers)
            json_data = json.loads(data.text)
        except Exception as e:
            print(e)

            return {"data": None, "coords": None, "num": i}
        # 存放时间序列
        list_time = list()
        # 存放指数
        list_data = list()
        for item in json_data['data']['curve']:  # 交通数据
            list_time.append(item['datatime'])
            list_data.append(item['congestIndex'])
        realdata = {"num": i, "time": list_time, "data": list_data}
        list_bounds = []
        for item in json_data['data']['location']:  # 卫星数据
            bound = {}
            for locations, count in zip(item.split(","), range(0, item.split(",").__len__())):
                if count % 2 != 0:

                    bound['lat']: float = locations  # 纬度

                else:
                    bound['lon']: float = locations  # 纬度
            list_bounds.append(bound)
        result = {"data": realdata, "coords": list_bounds, "num": i}

        return result

    def get_all_citycode(self) -> Iterator[CityInfo]:
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
