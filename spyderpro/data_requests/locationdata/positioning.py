import requests
import json
from spyderpro.port_connect.internet_connect import Connect
from spyderpro.data_instances.lbs import Geographi


class PeoplePositionin(Connect):
    """
    获取全国定位数据，此模块慎用
    """
    instance = None
    bool_instance_flag = False

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.bool_instance_flag = True
        return cls.instance

    def __init__(self):
        if PeoplePositionin.bool_instance_flag:
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'

            }
            PeoplePositionin.bool_instance_flag = False

    def get_people_positionin_data(self, rank: int, max_num=4) -> list:
        """

        :param rank: 第几块数据文件
        :param max_num: 把数据文件分割成几块
        :return list[dict,,,,,]
        注意，返回的第一个元素是搜索时间  {"搜索时间": realtime}
        """
        assert isinstance(max_num, int)
        assert isinstance(rank, int)
        # 请求链接
        str_href = 'https://xingyun.map.qq.com/api/getXingyunPoints'
        # 请求参数
        dict_query_string_parameters = {
            'count': max_num,  # 将整个数据文件切割成几份
            'rank': rank  # 设置请求第几个数据文件
        }

        response = requests.post(url=str_href, headers=self.headers, data=json.dumps(dict_query_string_parameters))
        if response.status_code != 200:
            return None
        json_data = json.loads(response.text)
        # realtime = g['time']  # 目前定位时间
        # yield {"搜索时间": realtime}
        flag = 0
        #维度
        float_lat = None
        #经度
        float_lon = None
        for item in iter(json_data['locs'].split(',')):
            flag += 1
            if flag == 1:
                try:
                    float_lat = float(item) / 100  # 纬度
                except ValueError:
                    continue
            if flag == 2:
                float_lon = float(item) / 100  # 经度
            if flag == 3:
                num = int(item)  # 人数
                flag = 0

                yield Geographi(latitude=float_lat, longitude=float_lon, number=num)
