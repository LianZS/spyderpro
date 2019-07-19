import random
import requests
import re
import datetime
from typing import Iterator
from bs4 import BeautifulSoup

'''获取2k多个城市的历史天气情况'''


class WeatherHistory(object):
    class weatherstatus:

        __slots__ = ['date', 'state', 'temperature', 'wind']

        def __init__(self, ddate, state, tempera, wind):
            self.date = ddate  # 日期
            self.state = state  # 天气状况
            self.temperature = tempera  # 气温
            self.wind = wind  # 风力风向

    def __init__(self):
        self.request = requests.Session()
        self.headers = {
            'Host': 'www.tianqihoubao.com',
            'User-Agent': 'Mozilla/5.0 (Macinto¬sh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/71.0.3578.98 Safari/537.36'
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
        :return:
        """
        url = 'http://www.tianqihoubao.com/lishi/'
        data = self.request.get(url=url, headers=self.headers)
        pre_url = 'http://www.tianqihoubao.com/'
        sounp = BeautifulSoup(data.content, 'lxml')  # 此处不要使用data.text，会出现乱码，改用response保证原有样子
        sounp.prettify()
        for res in sounp.find_all(name='a', href=re.compile('^/lishi.*[htm]$')):
            url_lis = list()
            url_lis.append(pre_url)
            url_lis.append(res['href'])
            url = ''.join(url_lis)  # 链接拼接
            dic = dict()
            province = res.string  # 省份
            dic['province'] = province
            dic['url'] = url
            yield dic

    def get_city_past_link(self, url: str) -> Iterator:
        """
        获取省份下所有城市分区链接
        :param url: 省份链接入口
        :return:list[{'url':,"city"}]
        """

        data = self.request.get(url=url, headers=self.headers)
        pre_url = 'http://www.tianqihoubao.com/'
        sounp = BeautifulSoup(data.content, 'lxml')  # 此处不要使用data.text，会出现乱码，改用response保证原有样子
        sounp.prettify()
        for res in sounp.find_all(name='dd'):
            res = res.find_all(name='a')
            for info in res:
                dic = dict()

                cityname = info.string  # 城市名字
                url_lis = list()
                url_lis.append(pre_url)
                url_lis.append(info['href'])
                url = ''.join(url_lis)  # 城区天气历史链接
                dic['url'] = url
                dic['city'] = cityname.strip(' ')
                yield dic

    def get_city_all_partition(self, url: str) -> Iterator:
        """
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
            'User-Agent': random.choice(self.use)
        }
        pre_url = "http://www.tianqihoubao.com/"
        try:
            data = requests.get(url=url, headers=headers)
            if data.status_code != 200:
                return "网络链接%d" % data.status_code
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
        sounp = BeautifulSoup(data.text, 'lxml')  # 此处不要使用data.text，会出现乱码，改用response保证原有样子
        sounp.prettify()
        content = sounp.find(name='div', attrs={"class": "wdetail"})
        tags = content.find_all(name="a")

        last = str(datetime.datetime.today().date()).replace("-", "")
        for tag in tags[:-2]:  # 将date这个说明跳过
            href = tag.get("href")
            if last in href:
                url = "http://www.tianqihoubao.com/lishi/" + href
            else:
                url = pre_url + href
            yield url

    def get_weather_detail(self, url) -> Iterator[weatherstatus]:
        """
        请求历史月份历史数据，'日期', '天气状况', '气温', '风力风向'
        :param url:
        :return: list[{'date', 'state', 'temperature', 'wind'}]
        {'date', 'state', 'temperature', 'wind'}->{'日期', '天气状况', '气温', '风力风向'}
        """

        response = self.request.get(url=url, headers=self.headers)
        if response.status_code != 200:
            print("%s请求--失败" % url)
            return None
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find(name="table")
        tr = table.find_all(name="tr")

        dates = table.find_all(name='a')
        state =None
        temperature = None
        wind = None
        for tds, date in zip(tr, dates):

            value = list()
            date = date.text
            date = re.sub("\s", '', date)

            value.append(date)
            count = 0
            for td in tds:

                text = str(td.string)
                text = text.replace(" ", "")

                if text == "\n" or text == "None":
                    continue
                text = re.sub("\s", "", text)
                count += 1

                if count == 1:
                    state = text
                elif count == 2:
                    temperature = text
                elif count == 3:
                    wind = text
                yield self.weatherstatus(ddate=date, state=state, tempera=temperature, wind=wind)


if __name__=="__main__":


    for item in WeatherHistory().get_weather_detail('http://www.tianqihoubao.com/lishi/beijing/month/201101.html'):
        print(item.temperature)
