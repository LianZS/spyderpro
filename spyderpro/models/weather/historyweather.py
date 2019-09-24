import random
import requests
import re
import os
import csv
import datetime
from typing import Iterator
from threading import Thread, Semaphore
from bs4 import BeautifulSoup
from spyderpro.models.weather.province import WeatherOfProvinceLink, WeatherOfCityLink

'''获取2k多个城市的历史天气情况'''


class WeatherStatus:
    __slots__ = ['date', 'state', 'temperature', 'wind']

    def __init__(self, ddate, state, tempera, wind):
        self.date = ddate  # 日期
        self.state = state  # 天气状况
        self.temperature = tempera  # 气温
        self.wind = wind  # 风力风向


class WeatherHistory(object):

    def __init__(self):
        self.request = requests.Session()
        self.headers = {

            'Host': 'www.tianqihoubao.com',
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'
        }
        self.useagent = ['Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
                         'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
                         'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:10.0) Gecko/20100101 Firefox/62.0',
                         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/71.0.3578.98 Safari/537.36',
                         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134']

    def get_province_link(self) -> Iterator:
        """
        获取进入每个城市具体的区域--***省份***---链接入口
        :return:{"province":,"url":}
        """
        # 获取所有省份链接
        href = 'http://www.tianqihoubao.com/lishi/'
        try:
            response = self.request.get(url=href, headers=self.headers)
        except requests.exceptions.ConnectionError:
            print("连接失败")
            return None

        except Exception as e:
            print(e)
            return None
        if response.status_code != 200:
            return None
        pre_url = 'http://www.tianqihoubao.com/'
        # 解析
        sounp = BeautifulSoup(response.content, 'lxml')  # 此处不要使用data.text，会出现乱码，改用response保证原有样子
        sounp.prettify()
        for res in sounp.find_all(name='a', href=re.compile('^/lishi.*[htm]$')):
            url_lis = list()
            url_lis.append(pre_url)
            url_lis.append(res['href'])
            url = ''.join(url_lis)  # 链接拼接
            province = res.string  # 省份
            yield WeatherOfProvinceLink(province=province, url=url)

    def get_city_past_link(self, url: str) -> Iterator:
        """
        获取省份下所有城市分区链接
        :param url: 省份链接入口
        :return:list[{'url':,"city"}]
        """
        try:
            response = self.request.get(url=url, headers=self.headers)
        except requests.exceptions.ConnectionError:
            print("连接失败")
            return None

        except Exception as e:
            print(e)
            return None
        if response.status_code != 200:
            return None
        pre_url = 'http://www.tianqihoubao.com/'
        sounp = BeautifulSoup(response.content, 'lxml')  # 此处不要使用data.text，会出现乱码，改用response保证原有样子
        sounp.prettify()
        for res in sounp.find_all(name='dd'):
            res = res.find_all(name='a')
            for info in res:
                cityname = info.string.strip(' ')  # 城市名字
                url_lis = list()
                url_lis.append(pre_url)
                url_lis.append(info['href'])
                href = ''.join(url_lis)  # 城区天气历史链接

                yield WeatherOfCityLink(city=cityname, url=href)

    def get_city_all_partition(self, url: str) -> Iterator:
        """
               url: http://www.tianqihoubao.com//lishi/bj.htm

               请求获取区域10多年来多每个月的天气数据链接
               :param url:
               :return: IIterator
               """
        result = self.__into_area(url)
        return result

    def __into_area(self, url) -> Iterator:
        """
        请求获取区域10多年来多每个月的天气数据链接
        :param url:
        :return: Iterator
        """
        headers = {
            'Host': 'www.tianqihoubao.com',
            'User-Agent': random.choice(self.useagent)
        }
        pre_url = "http://www.tianqihoubao.com/"
        try:
            response = requests.get(url=url, headers=headers)

        except ConnectionResetError:
            print("断网了")
            return ["ConnectionResetError"]

        except ConnectionError:
            print("该链接链接出现问题%s" % url)

            return ["ConnectionError"]
        except Exception as e:
            print(e)
            print("%s出问题了" % url)
            return ["Error --%s" % e]
        if response.status_code != 200:
            return "网络链接%d" % data.status_code
        # 解析
        sounp = BeautifulSoup(response.text, 'lxml')  # 此处不要使用data.text，会出现乱码，改用response保证原有样子
        sounp.prettify()
        content = sounp.find(name='div', attrs={"class": "wdetail"})
        tags = content.find_all(name="a")
        # 今天日期：yyyymmdd
        last = str(datetime.datetime.today().date()).replace("-", "")
        for tag in tags[:-2]:  # 将date这个说明跳过
            href = tag.get("href")
            if last in href:
                waether_url = "http://www.tianqihoubao.com/lishi/" + href
            else:
                waether_url = pre_url + href
            yield waether_url

    def get_weather_detail(self, url) -> Iterator[WeatherStatus]:
        """
        http://www.tianqihoubao.com//lishi/beijing/month/201102.html
        请求历史月份历史数据，'日期', '天气状况', '气温', '风力风向'
        :param url:
        :return: list[{'date', 'state', 'temperature', 'wind'}]
        {'date', 'state', 'temperature', 'wind'}->{'日期', '天气状况', '气温', '风力风向'}
        """
        try:
            response = self.request.get(url=url, headers=self.headers)
        except ConnectionResetError:
            print("断网了")
            return None

        except ConnectionError:
            print("该链接链接出现问题%s" % url)

            return ["ConnectionError"]
        except Exception as e:
            print(e)
            print("%s出问题了" % url)
            return None
        if response.status_code != 200:
            print("%s请求--失败" % url)

            return None
        # 解析
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find(name="table")
        tr = table.find_all(name="tr")

        state = None
        temperature = None
        wind = None
        for item in tr:
            if not item.td.a:
                continue
            # 时间
            cur_date = re.sub("\s", "", str(item.td.a.string))
            count = 0
            for t in item:
                if not t.string or t.string == "\n":
                    continue
                count += 1
                d = re.sub("\s", "", str(t.string))
                if count == 1:
                    state = d
                elif count == 2:
                    temperature = d
                elif count == 3:
                    wind = d
            yield WeatherStatus(ddate=cur_date, state=state, tempera=temperature, wind=wind)
