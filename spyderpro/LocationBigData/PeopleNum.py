import requests
import json
from spyderpro.Connect.InternetConnect import Connect


class PeoplePositionin(Connect):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'

        }

    def get_PeoplePositionin_data(self, rank: int, max_num=4) -> list:
        """

        :param rank: 第几块数据文件
        :param max_num: 把数据文件分割成几块
        :return list[dict,,,,,]
        注意，返回的第一个元素是搜索时间  {"搜索时间": realtime}
        """
        assert isinstance(max_num, int)
        assert isinstance(rank, int)
        href = 'https://xingyun.map.qq.com/api/getXingyunPoints'

        query_string_parameters = {
            'count': max_num,  # 将整个数据文件切割成几份
            'rank': rank  # 设置请求第几个数据文件
        }

        response = requests.post(url=href, headers=self.headers, data=json.dumps(query_string_parameters))
        g = json.loads(response.text)
        realtime = g['time']  # 目前定位时间
        yield {"搜索时间": realtime}
        flag = 0
        lat: float = None
        lon: float = None
        num: int = None
        for item in iter(g['locs'].split(',')):
            flag += 1
            if flag == 1:
                try:
                    lat = float(item) / 100  # 纬度
                except ValueError:
                    continue
            if flag == 2:
                lon = float(item) / 100  # 经度
            if flag == 3:
                num = int(item)  # 人数
                yield {"纬度": lat, "经度": lon, "人数": num}
                flag = 0
