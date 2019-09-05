import time
import requests
import re
import json
from datetime import datetime, timedelta

from urllib.parse import urlencode
from typing import Iterator, List, Dict
from spyderpro.portconnect.internetconnect import Connect
from spyderpro.portconnect.paramchecks import ParamTypeCheck
from spyderpro.instances.lbs import Trend, Geographi, Positioning


class PlaceInterface(Connect, ParamTypeCheck):
    instance = None
    bool_instance_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    # 获取所有省份
    def get_provinces(self) -> List:
        """
        获取所有省份
        :return: list
        """
        str_href = "https://heat.qq.com/api/getAllProvince.php?sub_domain="
        par: str = None
        dict_data = self.connect(par, str_href)
        list_data = [value["province"] for value in dict_data]
        return list_data

    # 所有城市
    def get_citys(self, province: str) -> List[Dict]:
        """
        获取省份下所有城市
        :param province: 省份名
        :return: list[{"province": , "city":}，，]
        """
        # 这里不需要quote中文转url，因为后面的urlencode自动会转

        dict_parameter = {
            "province": province,
            "sub_domain": ''
        }
        str_href = "https://heat.qq.com/api/getCitysByProvince.php?" + urlencode(dict_parameter)
        par: str = None
        dict_g = self.connect(par, str_href)
        list_of_dict_results = [{"province": province, "city": value["city"]} for value in dict_g]
        return list_of_dict_results

    def get_regions_bycity(self, province: str, city: str) -> List[Dict]:
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
        dict_parameter = {
            'province': province,
            'city': city,
            'sub_domain': ''
        }

        str_href = "https://heat.qq.com/api/getRegionsByCity.php?" + urlencode(dict_parameter)

        par: str = None
        # 获取返回数据
        dict_data = self.connect(par, str_href)
        # 用来存放数据
        list_data = list()
        for value in dict_data:
            str_placename = value['name']  # 地点
            int_placeid = value["id"]  # id
            dict_data = {'province': province, 'city': city, "place": str_placename, "id": int_placeid}
            list_data.append(dict_data)
        return list_data

    @staticmethod
    def get_bounds(pid: int) -> Dict:
        """
        获取某个地方地理位置数据
        :param pid:区域标识
        :return:
        """
        str_href = "https://heat.qq.com/api/getRegionHeatMapInfoById.php?id=" + str(pid)
        headers = dict()
        headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 ' \
                                     '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        response = requests.get(url=str_href, headers=headers).text
        json_data = json.loads(response)
        str_list_bounds = json_data['boundary']  # 格式'维度,经度|纬度,经度|'
        list_center = json_data['center_gcj'].split(',', 2)
        float_lat = float(list_center[0])  # 维度
        float_lon = float(list_center[1])  # 经度
        return {"bounds": str_list_bounds, "lat": float_lat, "lon": float_lon}


class PlaceTrend(PlaceInterface):
    """获取位置流量趋势"""

    def __init__(self, date_begin: str = None, date_end: str = None, intervallong: int = 5, user_agent: str = None):
        """
        时间段最长15天，最小时间间隔是1分钟range，开始时间最早2016-07-18
        :type date_begin: str
        :type date_end:str
        :type intervallong:int
        :param intervallong:数据间隔时间，最小为1分钟

        :param date_begin:开始搜索时间,格式yyyy-mm-dd
        :param date_end:结束搜索时间,格式yyyy-mm-dd
        :param user_agent:浏览器头
        """
        self.yyyy_mm_dd_date_begin = date_begin
        self.yyyy_mm_dd_date_end = date_end
        self.intervallong = intervallong
        if not PlaceTrend.bool_instance_flag:
            PlaceTrend.bool_instance_flag = True
            self.headers = dict()
            if user_agent is None:
                self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) ' \
                                                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 ' \
                                                  'Safari/537.36'

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
        # 请求参数
        dict_parameter = {
            'region': pid,
            'date_begin': self.yyyy_mm_dd_date_begin,
            'date_end': self.yyyy_mm_dd_date_end,
            'range': self.intervallong,
            'predict': False  # 是否获取预测数据,若为true，预测那天的键需要加上「预测」两字
        }
        # 请求链接
        str_href = "https://heat.qq.com/api/getLocation_uv_percent_new.php?" + urlencode(dict_parameter)
        par: str = None
        # 获取返回数据
        dict_data = self.connect(par, str_href)
        # 获取间隔日期 ----仅限于最大周期15天
        intervallong = timedelta(minutes=5)
        # # 时间从00：00：00开始计算，不管日期，这里只是为了取时间
        datetime_starttime = datetime(2019, 1, 1, 0, 0, 0)
        # 获取用户需要请求的日期时间
        for date in self.date_iterator():
            for index, detail_time in zip(dict_data[date],
                                          [str((datetime_starttime + intervallong * i).time()) for i in
                                           range(len(dict_data[date]))]):
                if index == "null":
                    break
                # 趋势结构体
                trend = Trend(pid=pid, place=region_name, date=int(date.replace("-", "")), index=float(index),
                              detailtime=detail_time)
                yield trend

    def date_iterator(self) -> Iterator[str]:
        """
        解析用户需要请求的时间，将yyyymmdd转为 yyyy-mm-dd格式
        :return:日期迭代器
        """
        # yyyymmdd转为yyyy-mm-dd格式
        str_format_date = time.strptime(self.yyyy_mm_dd_date_begin, "%Y-%m-%d")
        # 时间间隔
        timedelta_intervallong = timedelta(days=1)
        # 初始化时间
        init_date = datetime(str_format_date.tm_year, str_format_date.tm_mon, str_format_date.tm_mday)
        while 1:
            yyyy_mm_dd_date = str(init_date.date())
            if yyyy_mm_dd_date == self.yyyy_mm_dd_date_end:
                break
            yield yyyy_mm_dd_date
            # 下一刻时间
            init_date = init_date + timedelta_intervallong


class PlaceFlow(PlaceInterface):
    """
    获取地区人口分布情况数据
    """

    def __init__(self, user_agent: str = None):

        if not PlaceFlow.bool_instance_flag:
            PlaceFlow.bool_instance_flag = True
            self.headers = dict()
            if user_agent is None:
                self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/' \
                                                  '537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

            else:
                self.headers['User-Agent'] = user_agent
            self.headers['Host'] = 'heat.qq.com'

            self.request = requests.Session()

    def request_heatdata(self, url: str) -> Dict:
        """
        请求热力图数据
        :param url:热力图请求链接
        :return:dict热力图经纬度人数数据


        """
        try:
            response = self.request.get(url=url, headers=self.headers)
        except Exception as e:
            print(e)
            return {}
        if response.status_code == 200:
            # 热力图数据
            json_data = json.loads(response.text)
            return json_data
        else:
            return {}

    def get_heatdata_bytime(self, date: str, date_time: str, region_id: int):
        """
        某一时刻的人口分布详情
        :param date:日期：格式yyyy-mm-dd
        :param date_time:时间：格式hh:MM:SS
        :param region_id:地区唯一标识
        :return: dict经纬度人数数据，可能为{}
        """
        # 类型检查
        self.date_format_check(date)
        self.time_format_check(date_time)
        self.type_check(region_id, int)
        # 请求参数
        dict_paramer = {
            'region_id': region_id,
            'datetime': "".join([date, ' ', date_time]),
            'sub_domain': ''
        }
        # https://heat.qq.com/api/getHeatDataByTime.php?region_id=5381&datetime=2019-01-01+01%3A10%3A00&sub_domain=
        str_url = "https://heat.qq.com/api/getHeatDataByTime.php?" + urlencode(dict_paramer)
        # 请求热力图数据
        json_result = self.request_heatdata(str_url)
        return json_result

    @staticmethod
    def count_headdata(heatmap_data: dict, ddate: str, date_time: str, region_id: int) -> Positioning:

        """
        某一时刻的人数有多少
        :param heatmap_data: 热力图数据
        :param ddate:日期：格式yyyy-mm-dd
        :param date_time:时间：格式hh:MM:SS
        :param region_id:地区唯一表示
        :return:总人数
        """
        # 热力图数据
        dict_heatmap_data = heatmap_data
        if not dict_heatmap_data:
            return Positioning(None, None, None, None)
        int_total_num: int = sum(dict_heatmap_data.values())  # 总人数
        positioning = Positioning(region_id=region_id, date=int(ddate.replace("-", "")), detailtime=date_time,
                                  num=int_total_num)
        return positioning

    def complete_headata(self, heatmap_data: json) -> Iterator[Geographi]:
        """
        处理每个经纬度对应的人数
        :param heatmap_data:热力图数据
        :return:Iterator[Geographi]
        """
        # 经纬度围绕中心经纬度差*10000

        map_tuple__coords = map(self.deal_coordinates, heatmap_data.keys())

        for int_inv_lat, int_inv_lon in map_tuple__coords:
            key = '{0},{1}'.format(int_inv_lat, int_inv_lon)
            # 人数
            try:
                int_num = heatmap_data[key]
            except KeyError:
                continue
            # 经纬度人数结构体
            geographi = Geographi(latitude=float(int_inv_lat) / 10000, longitude=float(int_inv_lon) / 10000,
                                  number=int_num)
            yield geographi

    def complete_heatdata_simple(self, date: str, date_time: str, region_id: int) -> Iterator[Geographi]:
        """
           请求某一时刻的人数以及分布情况
           :param date:日期：格式yyyy-mm-dd
           :param date_time:时间：格式hh:MM:SS
           :param region_id:地区唯一表示
           :return:dict格式： Iterator[Geographi]->与中心经纬度的距离与相应人数
           """
        # 请求热力图数据
        heatmap_data = self.get_heatdata_bytime(date, date_time, region_id)
        # 处理热力图经纬度差数据，转为（维度，经度）数组map
        map_tuple_coords = map(self.deal_coordinates, heatmap_data.keys())  # 围绕中心经纬度加减向四周扩展

        for int_inv_lat, int_inv_lon in map_tuple_coords:
            key = '{0},{1}'.format(int_inv_lat, int_inv_lon)
            # 人数
            int_num: int = heatmap_data[key]
            # 经纬度人数结构体

            geographi = Geographi(latitude=float(int_inv_lat) / 10000, longitude=float(int_inv_lon) / 10000,
                                  number=int_num)
            yield geographi

    @staticmethod
    def deal_coordinates(coord):
        """
        将'维度,经度'转为tuple
        :param coord:
        :return:tuple（维度差，经度差）
        """
        if coord == ',':
            return (0, 0)
        tuple_escape = eval(coord)

        return tuple_escape

    def date_format_check(self, param):
        """日期类型格式检查
        :param param:日期参数
        """
        check = re.match("^\d{4}-\d{2}-\d{2}$", param)

        self.type_check(check, re.Match)

    def time_format_check(self, param):
        """
        时间类型格式检查
        :param param:时间参数
        :return:
        """
        check = re.match("^\d{2}:\d{2}:\d{2}$", param)

        self.type_check(check, re.Match)