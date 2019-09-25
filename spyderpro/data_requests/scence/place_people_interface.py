import requests
import json

from urllib.parse import urlencode
from typing import List, Dict
from spyderpro.port_connect.internet_connect import Connect
from spyderpro.port_connect.paramchecks import ParamTypeCheck


class PlacePeopleParentInterface(Connect, ParamTypeCheck):
    """
    通过腾讯地图获取景区客流量数据
    """
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
