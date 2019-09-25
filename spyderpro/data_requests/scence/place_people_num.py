import requests
import re
import json

from urllib.parse import urlencode
from typing import Iterator, Dict
from spyderpro.data_instances.lbs import Geographi, Positioning
from spyderpro.data_requests.scence._place_people_interface import _PlacePeopleParentInterface


class PlacePeopleNum(_PlacePeopleParentInterface):
    """
    获取地区人口分布情况数据
    """

    def __init__(self, user_agent: str = None):

        if not PlacePeopleNum.bool_instance_flag:
            PlacePeopleNum.bool_instance_flag = True
            self.headers = dict()
            if user_agent is None:
                self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/' \
                                             '537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

            else:
                self.headers['User-Agent'] = user_agent
            self.headers['Host'] = 'heat.qq.com'

            self.request = requests.Session()

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

    def get_heatdata_bytime(self, ddate: str, date_time: str, region_id: int):
        """
        某一时刻的人口分布详情
        :param date:日期：格式yyyy-mm-dd
        :param date_time:时间：格式hh:MM:SS
        :param region_id:地区唯一标识
        :return: dict经纬度人数数据，可能为{}
        """
        # 类型检查
        self.date_format_check(ddate)
        self.time_format_check(date_time)
        self.type_check(region_id, int)
        # 请求参数
        dict_paramer = {
            'region_id': region_id,
            'datetime': "".join([ddate, ' ', date_time]),
            'sub_domain': ''
        }
        # https://heat.qq.com/api/getHeatDataByTime.php?region_id=5381&datetime=2019-01-01+01%3A10%3A00&sub_domain=
        str_url = "https://heat.qq.com/api/getHeatDataByTime.php?" + urlencode(dict_paramer)
        # 请求热力图数据
        json_result = self.request_heatdata(str_url)
        return json_result

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
