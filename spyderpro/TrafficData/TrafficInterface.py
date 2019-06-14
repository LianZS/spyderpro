import json
import requests
import  abc
from urllib.parse import urlencode


class Traffic(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def citytraffic(self, citycode):
        pass

    # 道路数据获取
    @abc.abstractmethod
    def roaddata(self, citycode):
        pass

    @abc.abstractmethod
    def yeartraffic(self, citycode, year, quarter):
        pass

    # 经纬度查询
    @staticmethod
    def getlnglat(city):
        pre_url = 'https://apis.map.qq.com/jsapi?'
        req = {
            "newmap": 1,
            "qt": 'poi',
            "wd": city
        }
        headers = {'Host': 'apis.map.qq.com',
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 '
                                 '(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
        url = pre_url + urlencode(req)
        data = requests.get(url=url, headers=headers)
        g = json.loads(data.text)
        bounds = g['detail']['city']
        lon = bounds['pointx']
        lat = bounds['pointy']
        return {"lat": lat, "lon": lon}
