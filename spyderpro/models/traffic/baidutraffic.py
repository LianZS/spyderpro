import requests
import json
import time
from urllib.parse import urlencode
from typing import Dict, Iterator, List
from concurrent.futures import ThreadPoolExecutor
from spyderpro.models.traffic.road import Road, RoadData, RoadInfo
from spyderpro.models.traffic.trafficclass import TrafficClass, Year
from spyderpro.instances.infomation import CityInfo
from spyderpro.models.traffic.trafficinterface import Traffic


class BaiduTraffic(Traffic):

    def __init__(self):
        self.s = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/71.0.3578.98 Safari/537.36'

        }

    def city_daily_traffic_data(self, citycode: int, timetype='minute') -> Iterator[TrafficClass]:
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

        except requests.exceptions.ConnectionError:
            print("网络链接error")
            return iter([])
        except AttributeError:
            print("数据格式错误")
            return iter([])
        except json.JSONDecodeError:
            print("json解析异常")
            return iter([])
        except Exception as e:
            print(e)
            return iter([])
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

    def city_year_traffic_data(self, citycode: int, year: int = int(time.strftime("%Y", time.localtime())),
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
            json_data = json.loads(response.text)
            test = json_data['data']['list']  # 测试数据是否存在，失败说明请求失败
        except requests.exceptions.ConnectionError:
            print("网络链接error")
            return []
        except AttributeError:
            print("数据错误")
            return []
        except json.JSONDecodeError:
            print("json解析异常")
            return []
        except Exception as e:
            print(e)
            return []
        if not len(json_data):
            return []
        year = time.strftime("%Y-", time.localtime())  # 年份格式为2019-
        for item in json_data['data']['list']:
            # {'index': '1.56', 'speed': '32.83', 'time': '04-12'}
            date = year + item['time']
            float_index = float(item["index"])
            yield Year(pid=citycode, date=int(date.replace("-", "")), index=float_index)

    def city_road_traffic_data(self, citycode: int) -> Iterator[Road]:
        """
        获取拥堵道路前10名数据, 数据包括路名，速度，数据包，道路方向，道路经纬度数据

        :param citycode:城市id
        :return: iterable(Road)
        """

        iter_road_info: Iterator[RoadInfo] = self.__info_of_ten_roads(citycode)  # 请求道路数据, 获取道路信息包，包括道路pid，道路名，道路方向，速度
        if iter_road_info is None:
            print("参数不合法")
            yield None
            return
        list_raod_info = list(iter_road_info)

        iter_raod_data: Iterator[RoadData] = self.__get_realtime_road(list_raod_info, citycode)  # 请求并处理10条道路路实时路况数据

        list_raod_data: List[RoadData] = sorted(iter_raod_data, key=lambda x: x.num)  # 数据必须排序，不然和下面的信息不对称
        for road_info_obj, road_data_obj in zip(list_raod_info, list_raod_data):
            road_name = road_info_obj.road_name  # 路名
            speed = float(road_info_obj.road_speed)  # 速度
            # 'time':时间序列,'data":拥堵指数集},当请求失败时为None
            direction = road_info_obj.road_dir  # 道路方向
            rate = float(road_info_obj.cur_rate)  # 当前拥堵指数
            times_list = road_data_obj.detailt_time_list  # 时间列表

            bounds = json.dumps({"coords": road_data_obj.coords})  # 道路经纬度数据
            num = road_data_obj.num  # 排名
            data = road_data_obj.road_data_list  # 数据包,今天的拥堵指数集合数据

            road = Road(pid=citycode, roadname=road_name, speed=speed, dircetion=direction, bounds=bounds,
                        road_index_data_list=data, time_data_list=times_list, num=num, rate=rate)

            yield road

    def __info_of_ten_roads(self, citycode) -> Iterator[RoadInfo]:
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
            if response.status_code == 200:
                road_json_data = json.loads(response.text)
            else:
                road_json_data = {"status": 1}
        except requests.exceptions.ConnectionError:
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
        for item in road_json_data['data']['list']:
            road_id = item['roadsegid']
            road_name = item['roadname']
            road_dir = item["semantic"]  # 方向
            road_speed = item["speed"]  # 速度
            cur_rate = item['index']  # 当前拥堵指数
            coords = item['links']
            yield RoadInfo(road_name=road_name, road_dir=road_dir, road_speed=road_speed, road_id=road_id,
                           cur_rate=cur_rate, coords=coords)

    def __get_realtime_road(self, list_raod_info: List[RoadInfo], citycode) -> Iterator[RoadData]:
        """
           处理10条道路路实时路况数据
           :param list_raod_info:存放十条道路的基本信息
           :param citycode:城市id
           :return: Iterator[{"data": realdata, "coords": list_bounds, "num": i}]
           """
        pool = ThreadPoolExecutor(max_workers=10)
        # 存放任务对象
        reuslt_list = list()
        for road_info_obj, i in zip(list_raod_info, range(10)):
            dict_parameter = {
                'cityCode': citycode,
                'id': road_info_obj.road_id
            }
            road_url = 'https://jiaotong.baidu.com/trafficindex/city/roadcurve?' + urlencode(dict_parameter)

            t = pool.submit(self.__get_realtime_road_data, road_url, i)  # 请求该道路数据
            reuslt_list.append(t)
        for t in reuslt_list:
            # 返回结果
            yield t.result()

            # 道路请求

    def __get_realtime_road_data(self, road_url: str, i: int) -> RoadData:
        """
         具体请求某条道路的数据
         :param road_url:请求链接
         :param i: 排名

         """

        try:
            data = self.s.get(url=road_url, headers=self.headers)
            json_data = json.loads(data.text)
        except requests.exceptions.ConnectionError:
            print("网络链接error")
            return RoadData(num=i, detailt_time_list=None, road_data_list=None)
        except requests.exceptions.ChunkedEncodingError:
            print("网络链接error")
            return RoadData(num=i, detailt_time_list=None, road_data_list=None)
        except AttributeError:
            print("数据格式错误")
            return RoadData(num=i, detailt_time_list=None, road_data_list=None)
        except json.decoder.JSONDecodeError:
            return RoadData(num=i, detailt_time_list=None, road_data_list=None)
        except Exception as e:
            print(e)
            return RoadData(num=i, detailt_time_list=None, road_data_list=None)

        # 存放时间序列
        road_time_list = list()
        # 存放指数
        road_data_list = list()
        # 道路经纬度
        road_bounds_list = list()
        # 获取时间和拥堵指数
        for item in json_data['data']['curve']:  # 交通数据
            road_time_list.append(item['datatime'])
            road_data_list.append(item['congestIndex'])
        # 获取经纬度
        for item in json_data['data']['location']:  # 卫星数据
            bound = {}
            for locations, count in zip(item.split(","), range(0, item.split(",").__len__())):
                if count % 2 != 0:

                    bound['lat']: float = locations  # 纬度

                else:
                    bound['lon']: float = locations  # 纬度
            road_bounds_list.append(bound)
        road_data = RoadData(num=i, detailt_time_list=road_time_list, road_data_list=road_data_list,
                             coords=road_bounds_list)
        return road_data

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



