import requests
import time
import re
import json
from urllib.parse import urlencode


class Weather:

    def __init__(self):

        self.s = requests.Session()

        self.headers = {
            'Host': 'www.weather.com.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/71.0.3578.98 Safari/537.36'
        }
        self.use = ['Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
                    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:10.0) Gecko/20100101 Firefox/62.0',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/71.0.3578.98 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134']

    def weatherforcest(self, weatherpid: str) -> list:
        """
        获取天气数据
        :param weatherpid: id
        :return: iterable(dict)
        """

        url = "http://www.weather.com.cn/weather1d/" + weatherpid + ".shtml"
        data = self.s.get(url=url, headers=self.headers)
        par = re.compile('hour3data=(.*)')
        hour3data = re.search(par, data.content.decode("utf-8")).group(1)
        d = re.sub('=', ":", hour3data)
        g = json.loads(d)
        d = time.strftime("%Y-%m-", time.localtime(time.time()))
        for item in g['7d']:
            for element in item:
                # '12日20时,n00,晴,4℃,西北风,<3级'

                data = element.split(',')
                index = 0
                dic = {}
                for result in data[:-1]:
                    if index == 0:
                        day = result.split('日')
                        date = d + day[0]
                        detailtime = day[1]
                        dic['date'] = date
                        dic['detailTime'] = detailtime
                    elif index == 1:
                        index += 1
                        continue
                    elif index == 2:
                        state = result
                        dic['state'] = state
                    elif index == 3:
                        temperature = result
                        dic['temperature'] = temperature
                    elif index == 4:
                        wind = result
                        dic['wind'] = wind
                    index += 1
                yield dic

    def getWeatherId(self, name):
        """
        搜索该地方的天气id
        :param name: 地方名
        :return: str->id
        """
        parameter = {
            'cityname': name,

        }
        headers = {
            'Host': 'toy1.weather.com.cn',
            'Referer': 'http: // www.weather.com.cn / weather / 101310201.shtml',

            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }

        href = 'http://toy1.weather.com.cn/search?' + urlencode(parameter)
        response = self.s.get(url=href, headers=headers).text
        ID = re.search("(\d+\w)", response).group(1)
        return ID
