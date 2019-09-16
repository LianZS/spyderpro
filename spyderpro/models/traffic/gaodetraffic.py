import requests
import json
import time
from urllib.parse import urlencode
from typing import Iterator, Dict
from concurrent.futures import ThreadPoolExecutor
from spyderpro.models.traffic.trafficinterface import Traffic
from spyderpro.instances.trafficclass import TrafficClass, Road, Year


class GaodeTraffic(Traffic):

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
        str_href = "http://report.amap.com/ajax/cityHourly.do?cityCode=" + str(citycode)
        try:
            response = self.s.get(url=str_href, headers=self.headers)
            json_data = json.loads(response.text)
        except ConnectionError as e:

            print("编号%d--网络链接error:%s" % (citycode, e))

            return None
        date_today = time.strftime("%Y-%m-%d", time.localtime())  # 今天的日期

        date_yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 3600 * 24))  # 昨天的日期
        date = date_yesterday
        # 含有24小时的数据
        for item in json_data:
            detail_time = time.strftime("%H:%M", time.localtime(int(item[0]) / 1000))
            if detail_time == '00:00':
                date = date_today

            int_date = int(date.replace("-", ""))  # 日期
            float_index = float(item[1])  # 拥堵指数
            detail_time = detail_time + ":00"  # 具体时刻
            yield TrafficClass(citycode, int_date, float_index, detail_time)

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
            num = eval(data)['num']
            rate = float(item['index'])
            road = Road(pid=citycode, roadname=roadname, speed=speed, dircetion=direction, bounds=bounds, data=data,
                        num=num, rate=rate)

            yield road

    def __roads(self, citycode: int) -> Dict:
        """
        获取道路信息包，包括道路pid，道路名，道路方向，速度
        :param citycode:城市id
        :return:dict
        """

        dict_parameter = {
            "roadType": 0,
            "timeType": 0,
            "cityCode": citycode
        }
        str_href = "https://report.amap.com/ajax/roadRank.do?" + urlencode(dict_parameter)
        try:
            response = self.s.get(url=str_href, headers=self.headers)
        except requests.exceptions.ConnectionError:
            print("网络错误")
            return {}

        try:
            json_data = json.loads(response.text)  # 道路信息包
        except AttributeError:
            return {}
        list_id = []  # 记录道路pid
        list_roadname = []  # 记录道路名
        list_dir = []  # 记录道路方向
        list_speed = []  # 记录速度
        for item in json_data["tableData"]:
            list_roadname.append(item["name"])  # 道路名
            list_dir.append(item["dir"])  # 方向
            list_speed.append(item["speed"])  # 速度
            list_id.append(item["id"])  # 道路pid
        dict_collections = dict()  # 存放所有数据
        dict_collections["route"] = json_data['tableData']
        dict_collections["listId"] = list_id
        dict_collections["listRoadName"] = list_roadname
        dict_collections["listDir"] = list_dir
        dict_collections["listSpeed"] = list_speed

        return dict_collections

    def __realtimeroad(self, dic: dict, citycode: int) -> Iterator[dict]:
        """
        请求10条道路路实时路况数据
        :param dic:道路信息字典
        :param citycode:城市id
        """
        dict_parameter = {
            "roadType": 0,
            "timeType": 0,
            "cityCode": citycode,
            'lineCode': ''

        }
        str_href = "https://report.amap.com/ajax/roadDetail.do?" + urlencode(dict_parameter)
        pool = ThreadPoolExecutor(max_workers=10)
        # 存放任务对象
        reuslt_list = list()
        for pid, i in zip(dic["listId"],
                          range(0, (dic["listId"]).__len__())):
            str_road_url = str_href + str(pid)
            t = pool.submit(self.__realtime_roaddata, str_road_url, i)
            reuslt_list.append(t)
        for t in reuslt_list:
            # 返回结果
            yield t.result()

    def __realtime_roaddata(self, road_url: str, i: int):
        """
        具体请求某条道路的数据
        :param road_url: 道路数据链接
        :param i: 排名
        :return: dict->{"num": i, "time": time_list, "data": data}

        """

        try:
            response = self.s.get(url=road_url, headers=self.headers)
            json_data = json.loads(response.text)  # 拥堵指数
        except requests.exceptions.ConnectionError:
            print("网络链接error")
            return {"data": None, "num": i}
        except requests.exceptions.ChunkedEncodingError:
            print("网络链接error")
            return {"data": None, "num": i}
        except AttributeError:
            print("数据格式错误")
            return {"data": None, "num": i}

        list_data = []  # 拥堵指数
        list_time = []  # 时间
        for item in json_data:
            list_time.append(time.strftime("%H:%M", time.strptime(time.ctime(int(item[0] / 1000 + 3600 * 8)))))
            list_data.append(item[1])
        # {排名，时间，交通数据}
        real_data = {"num": i, "time": list_time, "data": list_data}
        result = {"data": real_data, "num": i}

        return result

    def yeartraffic(self, citycode: int, year: int = int(time.strftime("%Y", time.localtime())),
                    quarter: int = int(time.strftime("%m", time.localtime())) / 3) -> Iterator[Year]:
        """
        获取城市年度交通数据
        :param citycode: 城市id
        :param year: 年份
        :param quarter: 第几季度
        :return: iterable(dict)
        dict->{"date": date, "index": index, "city": name}
        """
        if quarter - int(quarter) > 0:

            quarter = int(quarter) + 1
        else:
            quarter = int(quarter)
        str_href = "http://report.amap.com/ajax/cityDailyQuarterly.do?"

        # year键表示哪一年 的数据
        dict_parameter = {
            "cityCode": citycode,
            "year": year,  # 年份
            "quarter": quarter  # 第几季
        }

        url = str_href + urlencode(dict_parameter)

        try:
            response = self.s.get(url=url, headers=self.headers)
            json_data = eval(response.text)
        except SyntaxError:
            print("高德地图年度数据请求失败！")
            return []
        except requests.exceptions.ConnectionError:
            print("网络链接error")
            return []
        except requests.exceptions.ChunkedEncodingError:
            print("网络链接error")
            return []
        except AttributeError:
            print("数据格式错误")
            return []
        try:
            test =json_data["categories"]
        except KeyError:
            print("请求失败")
            return []
        for date, index in zip(json_data["categories"], json_data['serieData']):
            yield Year(pid=citycode, date=int(date.replace("-", "")), index=index)
