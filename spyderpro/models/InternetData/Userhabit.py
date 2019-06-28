import requests
import json
import datetime
import re
from urllib.parse import urlencode
from bs4 import BeautifulSoup


class UserHabit:
    def __init__(self, user_agent=None):
        """

        :type user_agent: str
        :param:user_agent：浏览器
        """

        self.request = requests.Session()

        self.headers = dict()

        if user_agent is None:
            self.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 ' \
                                         '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

        else:
            self.headers['User-Agent'] = user_agent

    def get_user_portrait(self, year: int, startmonth: int = None, endmonth: int = None) -> list:
        """
        获取用户图像---性别分布 ，年龄分布，消费偏好，区域热度，应用偏好

        :param year:年份
        :param startmonth:开始月份
        :param endmonth:结束月份
        :rtype: iterable
        :return iterable[性别分布 ，年龄分布，消费偏好，区域热度，应用偏好.....{"区域热度 ": name, "占比": share}]
               """
        assert isinstance(year, int)
        assert isinstance(startmonth, int)
        if endmonth is not None:
            assert isinstance(endmonth, int)
        pre_url = 'http://mi.talkingdata.com/market-profile.json?'
        monthlist = self.monthset(year, startmonth, endmonth)  # 请求列表

        for date in monthlist:
            query_string_parameters = {
                'date': date
            }
            url = pre_url + urlencode(query_string_parameters)
            response = self.request.get(url=url, headers=self.headers)
            if response.status_code != 200:
                raise ConnectionError("网络请求"
                                      "出问题")
            result = json.loads(response.text)
            ages: list = result['age']  # 手机用户年龄段分布
            consumption: list = result['consumption']  # 消费偏好
            genders: list = result['gender']  # 性别分布
            preferences: list = result['preferences']  # 应用偏好
            provinces: list = result['provinces']  # 区域热度
            for age in ages:
                name = age['name']  # 年龄段
                share = age['share']  # 占比
                yield {"年龄段": name, "占比": share}
            for consum in consumption:
                name = consum['name']  # 消费偏好关键词
                share = consum['share']  # 占比
                yield {"消费偏好关键词": name, "占比": share}
            for gender in genders:
                name = gender['name']  # 性别
                share = gender['share']  # 占比
                yield {"性别": name, "占比": share}
            for preference in preferences:
                name = preference['name']  # 应用偏好
                share = preference['share']  # 占比
                yield {"应用偏好": name, "占比": share}
            for province in provinces:
                name = province['name']  # 区域热度
                share = province['share']  # 占比
                yield {"区域热度 ": name, "占比": share}

    def get_user_behavior(self, year: int, endmonth: int = None) -> list:
        """
        获取用户行为---人均安装应用趋势，人均启动应用趋势

        :param year:年份
        :param endmonth:月份
        :rtype: iterable
        :return iterable[{"日期": date, "人均安装应用": install, "人均启动应用": active}]     """
        assert isinstance(year, int)
        assert isinstance(endmonth, int)
        pre_url = 'http://mi.talkingdata.com/behavior.json?'
        monthlist = self.monthset(year, startmonth=endmonth)  # 以endmonth为结束点7个月每个月人均安装应用
        for date in monthlist:
            query_string_parameters = {
                'dateType': 'm',
                'endDate': date
            }
            url = pre_url + urlencode(query_string_parameters)
            response = self.request.get(url=url, headers=self.headers)
            if response.status_code != 200:
                raise ConnectionError("网络请求"
                                      "出问题")
            result = json.loads(response.text)
            for app in result:
                active = app['active']  # 人均启动应用
                date = app['date']  # 日期
                install = app['install']  # 人均安装应用
                yield {"日期": date, "人均安装应用": install, "人均启动应用": active}

    @staticmethod
    def monthset(year: int, startmonth: int, endmonth: int = None) -> list:
        """
        获取月份列表
        :param year: 年份
        :param endmonth:结束月份
        :type startmonth: int
        """
        monthlist = []  # 请求列表
        if year < 2014:
            raise TypeError("超过最低年限2014")
        if startmonth > 12 or startmonth < 1:
            raise TypeError("月份出错")
        if endmonth is None and startmonth is not None:
            date = datetime.date(year, startmonth, 1)
            monthlist.append(date)
        elif startmonth is None:
            raise TypeError("startmonth不能为空")
        elif startmonth > endmonth:
            raise TypeError("startmonth不能大于endmonth")
        else:
            seq: int = endmonth - startmonth + 1
            for month in range(seq):
                date = datetime.date(year, startmonth + month, 1)
                monthlist.append(date)
        return monthlist

    def get_similarapp_info(self, appname) -> list:
        """
        获取与该app名字相似的列表,及对应链接
        参考http://mi.talkingdata.com/app/trend/5.html
        :param appname:app名字
        :return:list[{"name":app名字,"href"：对应链接},,,]
        """
        url = "http://mi.talkingdata.com/search.html?keyword=" + appname
        response = self.request.get(url=url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        hrefs = soup.find_all(name='a', attrs={"href": re.compile("http://mi.talkingdata.com/app/")})
        datalist = list()
        for item in hrefs:
            name = item.get("title")
            href = item.get("href")
            dic = dict()
            dic['name'] = name
            dic['href'] = href
            datalist.append(dic)
        return datalist

    def request_app_data(self, appname, start_date, end_date):
        """
        获取该app的月活跃数，活跃用户率，时间列表，行业基准，行业均值
        :param appname:app名字
        :param start_date:开始月份 ，如2019-01-01，注意，日必须是月首日
        :param end_date:结束月份 ，如2019-04-01，注意，日必须是月首日
        :return:{'date': ['2018-12-01', ,,,], 'active': [660621779,,,,], 'active_rate': [0.4188573,,,,],
         'rate_hight': [0.0380731,,,], 'rate_low': [0.0007499, ,,,]}

        """
        url = self.get_similarapp_info(appname)[0]['href']
        response = self.request.get(url=url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        element = soup.find(name='li', attrs={"td-data": re.compile("\d+")})
        typeIds = element.get("td-data")
        query_string_parameters = {
            'typeIds': typeIds,
            "dateType": 'm',
            'endDate': end_date,
            'startDate': start_date
        }
        url = re.sub(".html", "/", url) + "allKpi.json?" + urlencode(query_string_parameters)
        response = self.request.get(url=url, headers=self.headers)
        data = json.loads(response.text)[0]
        active = data['active']  # 活跃用户数
        active_rate = data['activeRate']  # 活跃用户率
        datelist = data['date']  # 时间列表

        active_rate_benchmark_hight = data['activeRateBenchmarkH']  # 行业基准
        coverage_rate_ben_chmark_low = data['coverageRateBenchmarkL']  # 行业均值
        dic = dict()
        dic['date'] = datelist
        dic['active'] = active
        dic['active_rate'] = active_rate
        dic['rate_hight'] = active_rate_benchmark_hight
        dic['rate_low'] = coverage_rate_ben_chmark_low
        return dic

    def get_app_userhabit(self, appname, start_date):

        """
        获取app的用户画像数据,性别占比,年龄分布,省份覆盖率,app用户关键词
        参考http://mi.talkingdata.com/app/trend/appRank.json?appId=5&dateType=m&date=2018-11-01&typeId=101000
        :return:list[{gender:性别占比},{age"年龄分布},{:province省份覆盖率},{preference:app用户关键词}]
        """
        url = self.get_similarapp_info(appname)[0]['href']
        query_string_parameters = {
            "startTime": start_date
        }
        url = re.sub(".html", "", url) + ".json?" + urlencode(query_string_parameters)
        url = re.sub("trend", "profile", url)
        response = self.request.get(url=url, headers=self.headers).text
        data = json.loads(response)
        i = 0
        datalist = list()
        for appinfo in data:
            dl = list()
            profile_value = appinfo['profileValue']
            for item in profile_value:
                dic = dict()
                name = None  # 名称
                share = None  # 比例
                if i == 0:
                    continue
                elif i == 1:  # 性别占比
                    name = item['name']  # 性别
                    share = item['share']  # 比例
                elif i == 2:  # 年龄分布
                    name = item['name']  # 年龄
                    share = item['share']  # 比例
                elif i == 3:  # 省份覆盖率
                    name = item['code']  # 省份
                    share = item['share']  # 比例
                elif i == 4:
                    continue
                elif i == 5:
                    continue
                elif i == 6:  # app用户关键词
                    name = item['name']  # 关键词
                    share = item['share']  # 比例
                if name is not  None:
                    dic['name'] = name
                    dic['share'] = share
                dl.append(dic)
            if len(dl)>0:
                if i==1:
                    datalist.append({"gender":dl})
                elif i==2:
                    datalist.append({"age":dl})
                elif i==3:
                    datalist.append({"province":dl})
                elif i==6:
                    datalist.append({"preference":dl})

            i += 1
        return datalist


# d = UserHabit().get_app_userhabit('QQ', '2018-11-01')
# print(d)
