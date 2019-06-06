import requests
import json
import datetime
from urllib.parse import urlencode


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
        :rtype: list        """
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
        :param endmonth:结束月份
        :rtype: list        """
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
