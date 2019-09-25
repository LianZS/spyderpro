import requests
from typing import Iterator
from urllib.parse import urlencode
from spyderpro.port_connect.internet_connect import Connect
from spyderpro.data_instances.lbs import Positioning


class ScencePeopleFlow(Connect):
    """
    获取景区流量
    """

    def __init__(self, user_agent: str = None):
        self.request = requests.Session()
        self.headers = dict()
        if user_agent is None:
            self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 ' \
                                         '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

        else:
            self.headers['User-Agent'] = user_agent
        self.headers['Host'] = 'jiaotong.baidu.com'

    def peopleflow_info(self, peoplepid: int, ddate: int, historytype: int = 1) -> Iterator[Positioning]:
        """
        获取景区客流量
        :param peoplepid: 景区id
        :param historytype: 1表示现在的数据，2表示昨日数据，3表示最近的节假日数据
        :return: iter[Positioning,,]
        """
        #请求链接
        str_pre_url = 'http://jiaotong.baidu.com/trafficindex/dashboard/curve?'
        #请求参数
        dict_query_string_parameters = {
            'type': historytype,
            "area_type": "1",
            'area_id': str(peoplepid)
        }
        #构造请求链接
        str_url = str_pre_url + urlencode(dict_query_string_parameters)
        par: str = None
        g = self.connect(par, url=str_url)
        for item in g["data"]['list']:
            str_detailtime = item["data_time"].split(" ")[1] + ":00"  #字符串格式HH:MM:00

            int_num = int(item['count'])
            positioning = Positioning(region_id=int(peoplepid), date=ddate, detailtime=str_detailtime, num=int_num)

            yield positioning
            # yield {"时刻": detailtime, "客流量": num}

