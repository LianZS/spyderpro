import requests
from urllib.parse import urlencode
from spyderpro.Connect.InternetConnect import Connect


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

    def peopleflow_info(self, peoplepid):
        # type键 1 表示今天 2 表示昨天 3表示最近的节日
        pre_url = 'http://jiaotong.baidu.com/trafficindex/dashboard/curve?'
        u = {
            'type': '1',
            "area_type": "1",
            'area_id': str(peoplepid)
        }
        url = pre_url + urlencode(u)
        par: str = None
        g = self.connect(par, url=url)

        for item in g["data"]['list']:
            detailtime = item["data_time"].split(" ")[1]
            num = int(item['count'])
            yield {"时刻": detailtime, "客流量": num}
