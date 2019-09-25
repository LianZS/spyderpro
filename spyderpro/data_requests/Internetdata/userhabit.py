import requests
import json
import datetime
import re
from typing import Iterator
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from selenium import webdriver
from spyderpro.data_instances.userportrait import UserPortrait, UserBehavior, AppRateBenchmark, AppUserHabit


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
        self.headers['Host'] = 'mi.talkingdata.com'

    def get_user_portrait(self, year: int, startmonth: int = None, endmonth: int = None):
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
            map_age = map(lambda x: self.__map_filter(x, "age"), ages)
            map_consum = map(lambda x: self.__map_filter(x, "consum"), consumption)
            map_gender = map(lambda x: self.__map_filter(x, "sex"), genders)
            map_prefer = map(lambda x: self.__map_filter(x, "prefer"), preferences)
            map_provcince = map(lambda x: self.__map_filter(x, "province"), provinces)
            protrait = UserPortrait(map_age, map_consum, map_gender, map_prefer, map_provcince)
            yield protrait

    def __map_filter(self, param, param_name):
        return {param_name: param['name'], "value": param['share']}

    def get_user_behavior(self, year: int, endmonth: int = None) -> Iterator[UserBehavior]:
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
                behavior = UserBehavior(active, install, date)
                yield behavior

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

        driver = self.chrome()
        driver.get("http://mi.talkingdata.com/")
        element = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[2]/div/input")
        element.send_keys(appname)
        driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div/button').click()
        response = driver.page_source
        soup = BeautifulSoup(response, 'lxml')
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

    def get_app_active_info(self, appname, appid, start_date) -> AppRateBenchmark:
        """
        获取该app的月活跃数，活跃用户率，时间列表，行业基准，行业均值
        :param appname:app名字
        :param start_date:开始月份 ，如2019-01-01，注意，日必须是月首日
        :return:AppRateBenchmark

        """
        # url = self.get_similarapp_info(appname)[0]['href']
        paramer = {
            'typeIds': 101000,
            'dateType': 'm',
            'startDate': start_date
        }
        url = "http://mi.talkingdata.com/app/trend/" + str(appid) + "/allKpi.json?" + urlencode(paramer)

        response = self.request.get(url=url, headers=self.headers)
        data = json.loads(response.text)[0]
        try:
            active = data['active'][0]  # 活跃用户数
        except IndexError as e:
            print(url,e)
            return None

        active_rate = data['activeRate'][0]  # 活跃用户率
        datelist = data['date'][0]  # 时间列表

        active_rate_benchmark_hight = data['activeRateBenchmarkH'][0]  # 行业基准
        coverage_rate_ben_chmark_low = data['coverageRateBenchmarkL'][0]  # 行业均值
        # dic = dict()
        # dic['date'] = datelist
        # dic['active'] = active
        # dic['active_rate'] = active_rate
        # dic['rate_hight'] = active_rate_benchmark_hight
        # dic['rate_low'] = coverage_rate_ben_chmark_low

        appmark = AppRateBenchmark(appname, datelist, active, active_rate, active_rate_benchmark_hight,
                                   coverage_rate_ben_chmark_low)
        return appmark

    def get_app_userhabit(self, appname, pid, start_date) -> AppUserHabit:

        """
        获取app的用户画像数据,性别占比,年龄分布,省份覆盖率,app用户关键词
        参考http://mi.talkingdata.com/app/trend/appRank.json?appId=5&dateType=m&date=2018-11-01&typeId=101000
        :return:list[{gender:性别占比},{age"年龄分布},{:province省份覆盖率},{preference:app用户关键词}]
        :param start_date:yyyy-mm-dd
        """

        url = "http://mi.talkingdata.com/app/profile/" + str(pid) + ".json?startTime=" + start_date  # 后面改为从数据库提取链接
        response = self.request.get(url=url, headers=self.headers).text
        data = json.loads(response)
        i = 0
        ages = None
        gender = None
        preference = None
        province = None
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
                if name is not None:
                    dic['name'] = name
                    dic['share'] = share
                dl.append(dic)
            if len(dl) > 0:
                if i == 1:
                    # datalist.append({"gender": dl})
                    gender = dl
                elif i == 2:
                    ages = dl
                # datalist.append({"age": dl})
                elif i == 3:
                    province = dl
                # datalist.append({"province": dl})
                elif i == 6:
                    preference = dl
            # datalist.append({"preference": dl})

            i += 1
        app_habit = AppUserHabit(appname, ages, gender, preference, province, start_date)
        return app_habit

    @staticmethod
    def chrome():
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        driver = webdriver.Chrome()
        return driver

    def collectapp(self, pid):
        url = ''.join(['http://mi.talkingdata.com/app/trend/appRank.json?appId=', str(pid),
                       '&dateType=m&date=2018-11-01&typeId=101000'])
        d = requests.get(url=url)
        g = json.loads(d.text)

        try:
            result = g['appInfo']
        except KeyError:
            return None
        return result['appName']
