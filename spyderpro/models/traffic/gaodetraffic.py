import requests
import json
import time
from urllib.parse import urlencode
from typing import Iterator, List
from concurrent.futures import ThreadPoolExecutor
from spyderpro.models.traffic.trafficinterface import Traffic
from spyderpro.models.traffic.road import RoadData, RoadInfo, Road
from spyderpro.models.traffic.citytraffic import DayilTraffic, YearTraffic


class GaodeTraffic(Traffic):

    def __init__(self):
        self.s = requests.Session()
        self.headers = {
            'Host': 'report.amap.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/71.0.3578.98 Safari/537.36'

        }

    def city_daily_traffic_data(self, citycode: int) -> Iterator[DayilTraffic]:

        """获取实时交通状态，包括日期，拥堵指数，具体时刻
        Args:

          citycode:城市id
        Yields::
            返回TrafficClass类实例

        """
        str_href = "http://report.amap.com/ajax/cityHourly.do?cityCode=" + str(citycode)
        try:
            response = self.s.get(url=str_href, headers=self.headers)
            city_daily_traffic_json_data = json.loads(response.text)  # 请求成功时时list类型数据
            if isinstance(city_daily_traffic_json_data, dict):  # 请求失败时时dict类型
                raise ConnectionError
        except ConnectionError:

            print("标识:%d--网络连接error" % (citycode))

            return None
        except json.JSONDecodeError:
            print("json解析异常")
            return None
        except Exception as e:
            print(e)
            return None
        date_today = time.strftime("%Y-%m-%d", time.localtime())  # 今天的日期

        date_yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 3600 * 24))  # 昨天的日期
        date = date_yesterday
        # 含有24小时的数据

        for item in city_daily_traffic_json_data:
            detail_time = time.strftime("%H:%M", time.localtime(int(item[0]) / 1000))
            if detail_time == '00:00':
                date = date_today

            int_date = int(date.replace("-", ""))  # 日期
            float_index = float(item[1])  # 拥堵指数
            detail_time = detail_time + ":00"  # 具体时刻
            yield DayilTraffic(citycode, int_date, float_index, detail_time)

    def city_road_traffic_data(self, citycode: int) -> Iterator[Road]:
        """
        获取拥堵道路前10名数据, 数据包括路名，速度，数据包，道路方向，道路经纬度数据

        :param citycode:城市id
        :return: iterable(dict)
        dict->{"RoadName": roadname, "Speed": speed, "Direction": direction, "Bounds": bounds, 'Data': data}
        """
        iter_road_info: Iterator[RoadInfo] = self.__info_of_ten_roads(citycode)  # 10条道路基本信息

        if iter_road_info is None:
            print("参数不合法或者网络链接失败")
            return None
        list_raod_info = list(iter_road_info)
        iter_raod_data: Iterator[RoadData] = self.__get_realtime_road(list_raod_info, citycode)  # 请求10条道路路实时路况数据

        list_raod_data: List[RoadData] = sorted(iter_raod_data, key=lambda x: x.num)  # 数据必须排序，不然和下面的信息不对称
        for road_info_obj, road_data_obj in zip(list_raod_info, list_raod_data):
            road_name = road_info_obj.road_name  # 路名
            speed = float(road_info_obj.road_speed)  # 速度
            # 'time':时间序列,'data":拥堵指数集},当请求失败时为None
            direction = road_info_obj.road_dir  # 道路方向
            rate = float(road_info_obj.cur_rate)  # 当前拥堵指数
            times_list = road_data_obj.detailt_time_list  # 时间列表
            bounds = json.dumps({"coords": road_info_obj.coords})  # 道路经纬度数据
            num = road_data_obj.num  # 排名
            data = road_data_obj.road_data_list  # 数据包,今天的拥堵指数集合数据

            road = Road(pid=citycode, roadname=road_name, speed=speed, dircetion=direction, bounds=bounds,
                        road_index_data_list=data, time_data_list=times_list, num=num, rate=rate)

            yield road

    def city_year_traffic_data(self, citycode: int, year: int = int(time.strftime("%Y", time.localtime())),
                               quarter: int = int(time.strftime("%m", time.localtime())) / 3) -> Iterator[YearTraffic]:
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
            test = json_data["categories"]  # 测试数据是否存在，失败说明请求失败
            test2 = json_data['serieData']  # 测试数据是否存在，失败说明请求失败
        except SyntaxError:
            print("高德地图年度数据请求失败！")
            return None
        except requests.exceptions.ConnectionError:
            print("网络链接error")
            return None
        except requests.exceptions.ChunkedEncodingError:
            print("网络链接error")
            return None
        except AttributeError:
            print("数据格式错误")
            return None
        except json.JSONDecodeError:
            print("json解析异常")
            return None
        except Exception as e:
            print(e)
            return None

        for date, index in zip(json_data["categories"], json_data['serieData']):
            yield YearTraffic(pid=citycode, date=int(date.replace("-", "")), index=index)

    def __info_of_ten_roads(self, citycode: int) -> Iterator[RoadInfo]:
        """
        获取道路信息包，包括道路pid，道路名，道路方向，速度
        :param citycode:城市id
        :return:Iterator[RoadInfo]
        """

        dict_parameter = {
            "roadType": 0,
            "timeType": 0,
            "cityCode": citycode
        }
        str_href = "https://report.amap.com/ajax/roadRank.do?" + urlencode(dict_parameter)
        try:
            response = self.s.get(url=str_href, headers=self.headers)
            json_data = json.loads(response.text)  # 道路信息包
            test = json_data["tableData"]  # 测试存在该键
        except requests.exceptions.ConnectionError:
            print("网络错误")
            return None
        except json.JSONDecodeError:
            print("json解析异常")
            return None
        except KeyError:
            print("请求失败")
            return None
        except Exception as e:
            print("异常", e)
            return None

        for item in json_data["tableData"]:
            road_name = item["name"]  # 道路名
            road_dir = item["dir"]  # 方向
            road_speed = item["speed"]  # 速度
            road_id = item["id"]  # 道路pid
            cur_rate = item['index']  # 当前拥堵指数
            coords = item['coords']
            yield RoadInfo(road_name=road_name, road_dir=road_dir, road_speed=road_speed, road_id=road_id,
                           cur_rate=cur_rate, coords=coords)

    def __get_realtime_road(self, iter_road_info: Iterator[RoadInfo], citycode: int) -> Iterator[RoadData]:
        """
        请求10条道路路实时路况数据
        :param iter_road_info: Iterator[RoadInfo]
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

        i = 1  # 拥堵排名
        for road_info_obj in iter_road_info:
            pid = road_info_obj.road_id
            road_url = str_href + str(pid)
            t = pool.submit(self.__get_realtime_road_data, road_url, i)
            i += 1
            reuslt_list.append(t)

        for t in reuslt_list:
            # 返回结果
            yield t.result()

    def __get_realtime_road_data(self, road_url: str, i: int) -> RoadData:
        """
        具体请求某条道路的具体数据
        :param road_url: 道路数据链接
        :param i: 排名
        :return: RoadData

        """

        try:
            response = self.s.get(url=road_url, headers=self.headers)
            json_data = json.loads(response.text)  # 拥堵指数
        except requests.exceptions.ConnectionError:
            print("网络链接error")
            return RoadData(num=i, detailt_time_list=None, road_data_list=None)
        except requests.exceptions.ChunkedEncodingError:
            print("网络链接error")
            return RoadData(num=i, detailt_time_list=None, road_data_list=None)
        except AttributeError:
            print("数据格式错误")
            return RoadData(num=i, detailt_time_list=None, road_data_list=None)
        except json.JSONDecodeError:
            return RoadData(num=i, detailt_time_list=None, road_data_list=None)
        except Exception as e:
            print(e)
            return RoadData(num=i, detailt_time_list=None, road_data_list=None)
        road_data_list = []  # 拥堵指数
        road_time_list = []  # 时间
        for item in json_data:
            road_time_list.append(time.strftime("%H:%M", time.strptime(time.ctime(int(item[0] / 1000 + 3600 * 8)))))
            road_data_list.append(item[1])
        road_data = RoadData(num=i, detailt_time_list=road_time_list, road_data_list=road_data_list)
        return road_data
