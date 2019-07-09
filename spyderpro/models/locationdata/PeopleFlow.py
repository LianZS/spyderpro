import requests
from urllib.parse import urlencode
from spyderpro.portconnect.Internetconnect import Connect


class ScencePeopleFlow(Connect):
    def __init__(self, user_agent: str = None):
        self.request = requests.Session()
        self.headers = dict()
        if user_agent is None:
            self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 ' \
                                         '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

        else:
            self.headers['User-Agent'] = user_agent
        self.headers['Host'] = 'jiaotong.baidu.com'

    def peopleflow_info(self, peoplepid, historytype: int = 1):
        """
        获取景区客流量
        :param peoplepid: 景区id
        :param historytype: 1表示现在的数据，2表示昨日数据，3表示最近的节假日数据
        :return: Generator[时刻, 客流量]
        """
        #
        pre_url = 'http://jiaotong.baidu.com/trafficindex/dashboard/curve?'
        query_string_parameters = {
            'type': historytype,
            "area_type": "1",
            'area_id': str(peoplepid)
        }
        url = pre_url + urlencode(query_string_parameters)
        par: str = None
        g = self.connect(par, url=url)
        for item in g["data"]['list']:
            detailtime = item["data_time"].split(" ")[1]
            num = int(item['count'])
            yield detailtime, num
            # yield {"时刻": detailtime, "客流量": num}
